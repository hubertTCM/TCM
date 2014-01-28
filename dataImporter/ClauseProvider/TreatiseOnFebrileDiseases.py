# -*- coding: utf-8 -*-
import codecs
import os
import re
import sys

def append_ancestors_to_system_path(levels):
    parent = os.path.dirname(__file__)
    for i in range(levels):
        sys.path.append(parent)
        parent = os.path.abspath(os.path.join(parent, ".."))
        
append_ancestors_to_system_path(3)

from dataImporter.Utils.Utility import *

class FebribleDiseaseProvider:
    def __init__(self):
        self._source_file_fullpath = os.path.dirname(__file__) + '\\shl.txt'
        
    def __add_source_info__(self, clause):
        source = {u'comeFrom': {u'category': u'Book', u'name': u'伤寒论'}, u'author': u'张仲景'} 
        Utility.update_dict(clause, source)
        return clause
    
    def get_all_clauses(self):
        clauses = []
        
        shl = codecs.open(self._source_file_fullpath, 'r', 'utf-8')
        item_contents = []
        
        index = 0
        for line in shl:            
            matches = re.findall(ur"\s*[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u96f6]{1,3}\u3001", line)
            if len(matches) > 0 and line.strip().index(u'\u3001') < 4:
                if (len(item_contents) > 0):
                    clauses.append({'index':index, 'content':'\n'.join(item_contents)})
                index += 1
                item_contents = []
                
                item_contents.append(line.strip())
            else:    
                item_contents.append(line.strip())
        clauses.append({'index':index, 'content':'\n'.join(item_contents)})
        shl.close() 
                  
        map(self.__add_source_info__, clauses)
        return clauses

if __name__ == "__main__":
    provider = FebribleDiseaseProvider()
    clauses = provider.get_all_clauses()
    print clauses
    print "done"