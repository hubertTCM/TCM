# -*- coding: utf-8 -*-
import codecs
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

class FebribleDiseaseProvider:
    def __init__(self):
        self._source_file_fullpath = os.path.dirname(__file__) + '\\shl.txt'    
    
    def __create_caluse__(self, index, item_contents):
        items = [item.strip() for item in item_contents if len(item.strip()) > 0]
        comeFrom = {u'category': u'Book', u'name': u'伤寒论'} 
        content = ''
        if len(items) > 0:
            content = '\n'.join(items)
            parser = PrescriptionParser(content, u'方', QuantityAdjustor()) 
            prescriptions = parser.get_prescriptions() 
            for prescription in prescriptions:
                prescription.update({'comeFrom' : comeFrom})           
            
        return {'index':index, 'content':content, 'prescriptions':prescriptions, 'comeFrom' : comeFrom}
    
    def get_all_clauses(self):
        clauses = []
        
        shl = codecs.open(self._source_file_fullpath, 'r', 'utf-8')
        item_contents = []
        
        index = 0
        for line in shl:            
            matches = re.findall(ur"\s*[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u96f6]{1,3}\u3001", line)
            if len(matches) > 0 and line.strip().index(u'\u3001') < 4:
                if (len(item_contents) > 0):
                    clauses.append(self.__create_caluse__(index, item_contents))
                index += 1
                item_contents = []
                
                item_contents.append(line.strip())
            else:    
                item_contents.append(line.strip())
                
        shl.close() 
        
        clauses.append(self.__create_caluse__(index, item_contents))
        return clauses

if __name__ == "__main__":
    provider = FebribleDiseaseProvider()
    clauses = provider.get_all_clauses()    
    for item in clauses:
        print_prescription_list(item['prescriptions'])
        
#         for prescription in item['prescriptions']:
#             for component in prescription['components']:
#                 print component['unit']
    print "done"