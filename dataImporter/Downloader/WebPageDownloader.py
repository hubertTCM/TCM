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


from dataImporter.Utils.Utility import *

class DownloadItemProvider:
    def __init__(self, url):
        self._url = url
    
    def get_items(self): #url, category, title, local_folder
        return []

class ItemDownloader:
    def __init__(self, provider):
        self._source = provider
    
    def download(self):
        for item in provider.get_items():
            pass

if __name__ == "__main__":
    source_url = 'http://www.tcm100.com/user/lzznya/zzbook1.htm'
    #content = web_extractor.get_content_from(source_url)
    item = urlopen(source_url)
    content = item.read()
    item.close()
    
    to_file = codecs.open('test.html', 'w', 'utf-8', 'ignore')
    to_file.write(content)
    


