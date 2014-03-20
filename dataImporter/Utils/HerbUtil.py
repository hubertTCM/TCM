﻿# -*- coding: utf-8 -*-
import os
import re
import sys
from Utility import *

def append_ancestors_to_system_path(levels):
    parent = os.path.dirname(__file__)
    for i in range(levels):
        sys.path.append(parent)
        parent = os.path.abspath(os.path.join(parent, ".."))

append_ancestors_to_system_path(3)

reload(sys)
os.environ.update({"DJANGO_SETTINGS_MODULE":"TCM.settings"})

import TCM.settings
from TCM.models import *

class HerbUtility:
    def __init__(self):
        self._herbs=[] 
        self._herbs.extend([herb.name for herb in Herb.objects.all()])
        self._herbs.extend([herb.name for herb in HerbAlias.objects.all()])
        
    def get_all_herbs(self):
        return self._herbs
    
    def is_herb(self, name):
        return name in self.get_all_herbs()

class ItemAdjustor:
    def __init__(self, pattern, to_text_fetcher):
        self._pattern = pattern
        self._to_text_fetcher = to_text_fetcher
        
    def adjust (self, content):
        m = re.findall(self._pattern, content)
        if m:
            length = len(m)
            new_content = ""
            start_index = 0
            for i in range(length):
                sub_content = m[i]
                end_index = content.find(sub_content, start_index)
                new_content += content[start_index:end_index]
                new_content += self._to_text_fetcher(sub_content)#re.sub(' +', '', sub_content)
                start_index = end_index + len(sub_content)
                
            new_content += content[start_index:]
                
            return new_content
        else:
            return content
        
class BlankSpaceRemover:
    def __init__(self, patterns):
        self._patterns = patterns
        
#     def __adjust__(self, pattern, content):
#         m = re.findall(pattern, content)
#         if m:
#             length = len(m)
#             new_content = ""
#             start_index = 0
#             for i in range(length):
#                 sub_content = m[i]
#                 end_index = content.find(sub_content, start_index)
#                 new_content += content[start_index:end_index]
#                 new_content += re.sub(' +', '', sub_content)
#                 start_index = end_index + len(sub_content)
#                 
#             new_content += content[start_index:]
#                 
#             return new_content
#         else:
#             return content
        
    def adjust(self, content):
        for pattern in self._patterns:
            replacer = ItemAdjustor(pattern, Utility.remove_blank_space)
            content = replacer.adjust(content)
            #content = self.__adjust__(pattern, content)
        return content

class ItemReplaceAdjustor:
    def __init__(self, pairs):
        self._pairs = []
        self._pairs.extend(pairs)

    def adjust(self, content):
        for from_value, to_value in self._pairs:
            def value_fetcher(value):
                return to_value
            adjustor = ItemAdjustor(from_value, value_fetcher)
            content = adjustor.adjust(content)
        return content

class MedicalNameAdjustor:
    def __init__(self):
        self._split_items =[
                      (ur"甘草乌梅", ur"甘草 乌梅"),
                      (ur"干姜黄连", ur"干姜 黄连")
                      ]
        self._patterns = []
        herbUtility = HerbUtility()  
        for name in herbUtility.get_all_herbs():
            self._patterns.append(' *'.join(ch for ch in name))       
            
    def adjust(self, content):    
        remover = BlankSpaceRemover(self._patterns)           
        content = remover.adjust(content)
        ra = ItemReplaceAdjustor(self._split_items)
        content = ra.adjust(content)
        return content

if __name__ == "__main__":
    print "start"
#
#     line = ur"倭  硫黄                     干姜黄连   硫黄                2姜             黄连"
#     ma = MedicalNameAdjustor()
#     print ma.adjust(line)
#     items = re.split(ur"干姜黄连", line)
#     for item in items:
#         print item
    print "done"
    


