# -*- coding: utf-8 -*-
import codecs
import sys
import os
import re

reload(sys)
#sys.setdefaultencoding('utf-8')


def append_ancestors_to_system_path(levels):
    parent = os.path.dirname(__file__)
    for i in range(levels):
        sys.path.append(parent)
        parent = os.path.abspath(os.path.join(parent, ".."))
        
append_ancestors_to_system_path(3)

from dataImporter.Utils.Utility import *

class HerbAliasProvider:
    def __get_alias__(self, content, standard_name):
        pattern = ur'[ \u3000、]+'
        items = filter(lambda(x):len(x)>0 and standard_name != x, [Utility.remove_blank_space(item.strip()) for item in re.split(pattern, content)])
        return items
        
    def get_all_alias_pair(self):
        parent = os.path.dirname(__file__)
        #herb_folder = os.path.abspath(os.path.join(parent, u"..\HerbProvider"))
        alias_file_path = os.path.join(parent, "Alias.txt")
        
        alias_file = codecs.open(alias_file_path, 'r', 'utf-8', 'ignore')
        
        for line in alias_file: 
            pattern = ur"(混淆品：)*([^（）：]+)：\W+处方别名：(\W+)"       
            m = re.compile(pattern).match(line)
            if m: #medical(other)
                standard_name = m.group(2).strip()
                standard_name = re.sub('[ \u3000]+', '', standard_name)
                for alias in self.__get_alias__(m.group(3), standard_name):
                    yield alias, standard_name
            
        alias_file.close()
        
    
if __name__ == "__main__":
#     
#    lines = [ur"混淆品：关白附：为毛茛科植物黄花乌头的块根。处方别名：关白附、竹节白附",
#              ur"混混品：关白附：为毛茛科植物黄花乌头的块根。处方别名：关白附、竹节白附",
#              ur"党  参：为桔梗科植物党参、素花党参、川党参的根。处方别名：党参、台党、潞党参、西党、汉中党、文党、文元党、晶党、东党、辽党、中灵草、上党人参"]
#     for line in lines:
#         pattern = ur"(混淆品：)*([^（）：]+)：\W+处方别名：(\W+)"       
#         m = re.compile(pattern).match(line)
#         if m: #medical(other)
#             standard_name = m.group(2).strip()
#             standard_name = re.sub('[ \u3000]+', '', standard_name)
#             print standard_name
#             #for item in self.__get_alias__(m.group(2)):
#                 #print item
#             print m.group(3).strip()
#             print ""
    
    
    p = HerbAliasProvider()
    for alias, standard_name in p.get_all_alias_pair():
        print alias, ":", standard_name