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
    def download_single_file(self, url, local_path):
        parent = os.path.dirname(local_path)
        if not os.path.exists(parent):
            os.makedirs(parent)       
        
        content = web_extractor.get_content_from(url)
        to_file = codecs.open(local_path, 'w', 'utf-8', 'ignore')
        to_file.write(content)
        to_file.close()
    
    def download(self, provider):
        for item in provider.get_items():
            self.download_single_file(item['url'], item['local_path'])

if __name__ == "__main__":
    parent = os.path.dirname(__file__)
    consiliar_folder = os.path.abspath(os.path.join(parent, u"..\ConsiliaProvider"))
    file_name = os.path.join(consiliar_folder, u"外台秘要\index.html")
    downloader = ItemDownloader()
    source_url = 'http://www.tcm100.com/user/wtmy/index.htm' #
    #downloader.download_single_file(source_url, file_name)
    #root.xpath('//table[@cellpadding=2]//a')
    config = {
                    'xpath':'//table[@cellpadding=2]//a',
                    'extract_attributes':[{'source_attri' : 'href', 'target_attri_name':'url'},
                                          {'target_attri_name':'name'}
                                        ]
                }   
    provider = DownloadItemProvider(file_name, config)
    provider.get_items()
    print "done"
    


