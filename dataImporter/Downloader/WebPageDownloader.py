# -*- coding: utf-8 -*-
import codecs
import os
import re
import sys

from StringIO import StringIO
from urllib2 import urlopen

def append_ancestors_to_system_path(levels):
    parent = os.path.dirname(__file__)
    for i in range(levels):
        sys.path.append(parent)
        parent = os.path.abspath(os.path.join(parent, ".."))

append_ancestors_to_system_path(3)

from dataImporter.Utils.WebUtil import *
from dataImporter.Utils.HerbUtil import BlankSpaceRemover, MedicalNameAdjustor
        
class HTMLToText:
    def __init__(self, source_folder, config):
        self._config = config
        index_file_name = os.path.join(source_folder, "index_source.txt")
        self._source_file_names = []
        index_file = codecs.open(index_file_name, 'r', 'utf-8', 'ignore')
        
        if 'adjustors' in config:
            self._adjustors = config['adjustors']
            del config['adjustors']
        else:
            self._adjustors = []
        
        for line in index_file:
            try:
                value = Utility.get_dict_from(line.strip())
                self._source_file_names.append(os.path.join(source_folder, value['name'].strip()+".html"))          
            except Exception,ex:
                print "***" + line
                print Exception,":",ex

        index_file.close()
        
    def __get_content_from__(self, file_name):        
        source_file = codecs.open(file_name, 'r', 'utf-8', 'ignore')
        content = source_file.read()
        root = web_extractor.get_html_root_from_content(content)
        values = web_extractor.get_values_from_html_tree(root, self._config)
        if len(values) == 1:
            return values[0]['content']
        return ''
    
    def __adjust_content__(self, content):
        for adjustor in self._adjustors:
            content = adjustor.adjust(content)
        return content
    
    def convert(self):
        for source_file_name in self._source_file_names:
            if source_file_name.find("index")> 0:
                continue
            
            content = self.__get_content_from__(source_file_name)
            content = self.__adjust_content__(content)
            
            to_file_name = source_file_name[:source_file_name.index(".")] + ".txt"          
            txt_file = codecs.open(to_file_name, 'w', 'utf-8', 'ignore')
            txt_file.write(content)
            txt_file.close()
            
class DownloadItemProvider:
    def __init__(self, source_folder, config):
        self._source = os.path.abspath(os.path.join(source_folder, 'index.html'))#source
        self._config = config
        
    def __get_content__(self):
        source_file = codecs.open(self._source, 'r', 'utf-8', 'ignore')
        content = source_file.read()
        source_file.close()
        return content
    
    def get_items(self): #url, local_path
        content = self.__get_content__()
        root = web_extractor.get_html_root_from_content(content)
        values = web_extractor.get_values_from_html_tree(root, self._config)
        
        directory_name = os.path.dirname(self._source)
        to_file_name = os.path.abspath(os.path.join(directory_name, 'index_source.txt'))
        to_file = codecs.open(to_file_name, 'w', 'utf-8', 'ignore')
        for value in values:
            line = Utility.convert_dict_to_string(value) + '\n'
            to_file.write(line)
        to_file.close()
        
        return []

class ItemDownloader:  
    def __init__(self, folder_name):
        self._folder_name = folder_name  
        
    def download_single_file(self, url, file_name):
        if not os.path.exists(self._folder_name):
            os.makedirs(self._folder_name)       
        
        file_path = os.path.join(self._folder_name, file_name)      
        content = web_extractor.get_content_from(url)
        to_file = codecs.open(file_path, 'w', 'utf-8', 'ignore')
        to_file.write(content)
        to_file.close()
    
    def download_files_in_index_file(self):
        index_file_name = os.path.join(self._folder_name, "index_source.txt")
        index_file = codecs.open(index_file_name, 'r', 'utf-8', 'ignore')
        
        for line in index_file:
            try:
                value = Utility.get_dict_from(line.strip())
                self.download_single_file(value['url'].strip(), value['name'].strip()+".html")            
            except Exception,ex:
                print "***" + line
                print Exception,":",ex

        index_file.close()
        
if __name__ == "__main__":
    print "start"
    parent = os.path.dirname(__file__)
    consiliar_folder = os.path.abspath(os.path.join(parent, u"..\ConsiliaProvider"))
    yz_config = {
                    'xpath':'//table[@cellpadding=2]//a',
                    'extract_attributes':[{'source_attri' : 'href', 'target_attri_name':'url'},
                                          {'target_attri_name':'name'}
                                        ]
                } 
    fjx_config = {
                    'xpath':'//table[@cellpadding=0]//a',
                    'extract_attributes':[{'source_attri' : 'href', 'target_attri_name':'url'},
                                          {'target_attri_name':'name'}
                                        ]
                }   

    herb_folder = os.path.abspath(os.path.join(parent, u"..\HerbProvider"))
    clause_folder = os.path.abspath(os.path.join(parent, u"..\ClauseProvider"))
    prescription_folder = os.path.abspath(os.path.join(parent, u"..\PrescriptionProvider"))

    index_urls = []
    #index_urls.append(('http://www.tcm100.com/user/yzheng/index.htm', os.path.join(herb_folder, "yz"), yz_config )) #药征
    index_urls.append(('http://www.tcm100.com/user/wbtb/index.htm', os.path.join(clause_folder, "wbtb"), yz_config)) #温病条辨
    
    for url, folder, config in index_urls:
        pass
#         downloader = ItemDownloader(folder)
#         downloader.download_single_file(url, 'index.html')
#               
#         provider = DownloadItemProvider(folder, config)
#         provider.get_items()
#         
#         downloader.download_files_in_index_file()  
            
    adjustors = [ 
                 MedicalNameAdjustor(),
                 BlankSpaceRemover([ur"(（[^（）\n]+）)", ur"\n[^（）\n]+[。方] *\n"])
                 ]
    config = {
                'xpath':'//div[@class="content"]',
                'extract_attributes':[{'target_attri_name':'content', 'include_text_from_descendant':True}
                                    ],
                'adjustors':adjustors
                } 
      
    convertor = HTMLToText(os.path.join(clause_folder, 'wbtb'), config)
    convertor.convert() 
    
#      
#     items = [
#              ur"半夏（六钱）                        秫米（一两） 白芍（六钱）    桂枝（四钱， 桂枝少于                                  白芍者，表里异治也）              炙甘草（一钱） 生姜（三钱） 大枣（去核，二枚）",
#              ur"桂枝 （四钱，虽云                          桂枝汤），却用小建中汤法。 桂枝少于 白芍者，表里异治也                     end",
#              ur"桂枝          四钱，虽云 桂枝汤，      却用小建中汤法。 桂枝少于 白芍者，表里异治也                     end",
#             ur"绵茵陈  白芷 北  秦皮  茯苓皮  黄柏  藿香"]
#  
#     patterns=[
#               ur"(（[^（）]+）)", 
#               ur"[^（）]+[。方]"
#               ]
#      
#     a = BlankSpaceRemover(patterns)
#     for item in items:
#         line = item
#         print a.adjust(item)
    
    print "done"
    


