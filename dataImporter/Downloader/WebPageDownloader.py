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
    def __init__(self, url):
        self._url = url
    
    def get_items(self): #url, category, title, local_folder
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
    print os.path.abspath(os.path.join(parent, "..\hello"))
    file_name = os.path.abspath(os.path.join(parent, u"..\ConsiliaProvider\外台秘要\index.html"))
    downloader = ItemDownloader()
    source_url = 'http://www.tcm100.com/user/wtmy/index.htm' #
    downloader.download_single_file(source_url, file_name)
    print "done"
    


