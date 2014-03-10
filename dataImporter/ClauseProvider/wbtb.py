# -*- coding: utf-8 -*-
import codecs
import fnmatch
import os
import re
import sys

from PrescriptionParser import *

def append_ancestors_to_system_path(levels):
    parent = os.path.dirname(__file__)
    for i in range(levels):
        sys.path.append(parent)
        parent = os.path.abspath(os.path.join(parent, ".."))
        
append_ancestors_to_system_path(3)

from dataImporter.Utils.Utility import *
from dataImporter.Utils.WebUtil import *

class MedicalNameAdjustor:
    def __init__(self):
        medical_names = [u'飞 滑石', 
                    u'白 通草',
                    u'熟 附子',
                    u'生 附子',
                    u'生 石膏',
                    u'生 白芍',
                    u'炒 白芍',
                    u'炙 甘草',
                    u'藏 红花']
        self._medical_name_map = {}
        for item in medical_names:
            self._medical_name_map[item] = re.sub(' +', '', item)
            
    def adjust(self, content):    
        for key, value in self._medical_name_map.items():
            content = content.replace(key, value)
        
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
            
class wbtb_provider:
    def __init__(self, source_folder):
        index_file_name = os.path.join(source_folder, "index_source.txt")
        self._source_file_names = []
        index_file = codecs.open(index_file_name, 'r', 'utf-8', 'ignore')
        for line in index_file:
            try:
                value = Utility.get_dict_from(line.strip())
                self._source_file_names.append(os.path.join(source_folder, value['name'].strip()+".txt"))          
            except Exception,ex:
                print "***" + line
                print Exception,":",ex

        index_file.close()

    def __create_caluse__(self, index, item_contents):
        pass 
        
    def __get_clauses_from__(self, file_name):
        clauses = []
        
        source_file = codecs.open(file_name, 'r', 'utf-8')
        item_contents = []
        
        index = 0
        for line in source_file:            
            matches = re.findall(ur"\s*[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u96f6]{1,3}\u3001", line)
            if len(matches) > 0 and line.strip().index(u'\u3001') < 4:
                if (len(item_contents) > 0):
                    clauses.append(self.__create_caluse__(index, item_contents))
                index += 1
                item_contents = []
                
                item_contents.append(line.strip())
            else:    
                item_contents.append(line.strip())
                
        source_file.close
            
    def get_all_clauses(self):
        for file_name in self._source_file_names:
            self.__get_clauses_from__(file_name)
                
if __name__ == "__main__":
    source_folder = os.path.dirname(__file__)
    source_folder = os.path.join(source_folder, 'wbtb')
    
    adjustors = [MedicalNameAdjustor()]
    config = {
                'xpath':'//div[@class="content"]',
                'extract_attributes':[{'target_attri_name':'content', 'include_text_from_descendant':True}
                                    ],
                'adjustors':adjustors
                } 
     
    convertor = HTMLToText(source_folder, config)
    convertor.convert()
    
    provider = wbtb_provider(source_folder)
    provider.get_all_clauses()
    print "done"