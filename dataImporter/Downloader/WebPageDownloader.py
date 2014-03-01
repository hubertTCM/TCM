# -*- coding: utf-8 -*-
import codecs
import os
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

class DownloadItemProvider:
    def __init__(self, source, config):
        self._source = source
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
            line = Utility.print_dict(value) + '\n'
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
    file_name = os.path.join(consiliar_folder, u"外台秘要\index.html")
    source_url = 'http://www.tcm100.com/user/wtmy/index.htm' 

#     config = {
#                     'xpath':'//table[@cellpadding=2]//a',
#                     'extract_attributes':[{'source_attri' : 'href', 'target_attri_name':'url'},
#                                           {'target_attri_name':'name'}
#                                         ]
#                 }   
#     provider = DownloadItemProvider(file_name, config)
#     provider.get_items()
    
    
    downloader = ItemDownloader(os.path.join(consiliar_folder, u"外台秘要"))
    downloader.download_files_in_index_file()
    print "done"
    


