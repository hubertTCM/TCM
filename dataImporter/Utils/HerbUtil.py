# -*- coding: utf-8 -*-
import os
import re
import sys


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
        self._patterns = []
        herbUtility = HerbUtility()   
        for name in herbUtility.get_all_herbs():
            self._patterns.append(' *'.join(ch for ch in name))       
            
    def adjust(self, content):    
        remover = BlankSpaceRemover(self._patterns)           
        content = remover.adjust(content)
        
        return content

if __name__ == "__main__":
    print "start"
    print "done"
    


