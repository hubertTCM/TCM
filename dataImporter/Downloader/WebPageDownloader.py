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

class BlankSpaceRemover:
    def __init__(self, patterns):
        self._patterns = patterns
        
    def __adjust__(self, pattern, content):
        m = re.findall(pattern, content)
        if m:
            length = len(m)
            new_content = ""
            start_index = 0
            for i in range(length):
                sub_content = m[i]
                end_index = content.find(sub_content, start_index)
                new_content += content[start_index:end_index]
                new_content += re.sub(' +', '', sub_content)
                start_index = end_index + len(sub_content)
                
            new_content += content[start_index:]
                
            return new_content
        else:
            return content
        
    def adjust(self, content):
        for pattern in self._patterns:
            content = self.__adjust__(pattern, content)
        return content


class MedicalNameAdjustor:
    def __init__(self):
        medical_names = [
                    ur'飞滑石', 
                    ur'白通草',
                    ur'熟附子',
                    ur'生附子',
                    ur'生石膏',
                    ur'生白芍',
                    ur'炒白芍',
                    ur'炙甘草',
                    ur'藏红花',
                    ur'京三棱',
                    ur'生牡蛎',
                    ur'真阿胶',
                    ur'鲜竹叶心',
                    ur'绵茵陈',
                    ur'北秦皮',
                    ur'生黄柏']
        self._patterns = []
        for name in medical_names:
            self._patterns.append(' *'.join(ch for ch in name))
    
    def __adjust__(self, content):
#         #
#         #绵茵陈白芷北秦皮茯苓皮黄柏藿香
#         #人参山药茯苓莲子芡实补骨脂苁蓉萸肉五味子巴戟天菟丝子覆盆子
#         #熟地白芍附子五味炮姜茯苓
#         #熟地黄禹余粮五味子
#         #人参白芍附子茯苓炙甘草五味子
#         #川连黄芩干姜银花楂炭白芍木香汁
#         #
#         pairs = []
#         pairs.append(u'绵茵陈白芷北秦皮茯苓皮黄柏藿香', u'绵茵陈 白芷 北秦皮 茯苓皮 黄柏 藿香')
#         pairs.append(u'人参山药茯苓莲子芡实补骨脂苁蓉萸肉五味子巴戟天菟丝子覆盆子', u'人参 山药 茯苓 莲子 芡实 补骨脂 苁蓉 萸肉 五味子 巴戟天 菟丝子 覆盆子')
#         pairs.append(u'熟地白芍附子五味炮姜茯苓', u'熟地 白芍 附子 五味 炮姜 茯苓')
#         pairs.append(u'熟地黄禹余粮五味子', u'熟地黄 禹余粮 五味子')
#         pairs.append(u'人参白芍附子茯苓炙甘草五味子', u'人参 白芍 附子 茯苓 炙甘草 五味子')
#         pairs.append(u'川连黄芩干姜银花楂炭白芍木香汁', u'川连 黄芩 干姜 银花 楂炭 白芍 木香汁')
#         
#         adjustor_map = {}
#         for key, value in pairs:
#             adjustor_map[' *'.join(ch for ch in key)] = value
#         
#         for pattern, value in adjustor_map.items():
#             m = re.findall(pattern, content)
#             if m:
#                 length = len(m)
#                 new_content = ""
#                 start_index = 0
#                 for i in range(length):
#                     sub_content = m[i]
#                     end_index = content.find(sub_content, start_index)
#                     new_content += content[start_index:end_index]
#                     new_content += value
#                     start_index = end_index + len(sub_content)
#                     
#                 new_content += content[start_index:]
#                     
#                 return new_content
#             else:
#                 return content

        return content
    
            
    def adjust(self, content):    
        remover = BlankSpaceRemover(self._patterns)           
        content = remover.adjust(content)
        
        return content
        
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
                 BlankSpaceRemover([ur"(（[^（）]+）)", u"\n[^（）]+[。]\n"]),
                 MedicalNameAdjustor()
                 ]
    config = {
                'xpath':'//div[@class="content"]',
                'extract_attributes':[{'target_attri_name':'content', 'include_text_from_descendant':True}
                                    ],
                'adjustors':adjustors
                } 
      
    convertor = HTMLToText(os.path.join(clause_folder, 'wbtb'), config)
    convertor.convert() 
    
    
    items = [u"半夏（六钱）                        秫米（一两） 白芍（六钱）    桂枝（四钱， 桂枝少于                                  白芍者，表里异治也）              炙甘草（一钱） 生姜（三钱） 大枣（去核，二枚）",
             u"桂枝 （四钱，虽云                          桂枝汤），却用小建中汤法。 桂枝少于 白芍者，表里异治也                     end",
             u"桂枝          四钱，虽云 桂枝汤，      却用小建中汤法。 桂枝少于 白芍者，表里异治也                     end"]

    patterns=[ur"(（[^（）]+）)",
              u"\n[^（）]+\n"
              ]
    
    a = BlankSpaceRemover(patterns)
    for item in items:
        line = item
        print a.adjust(item)
    
    print "done"
    


