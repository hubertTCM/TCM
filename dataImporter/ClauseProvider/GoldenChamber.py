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


class GoldenChamberProvider:
    def __init__(self):
        self._source_file_fullpath = os.path.dirname(__file__) + '\\jkyl.txt'
        self._source = {u'comeFrom': {u'category': u'Book', u'name': u'金匮要略'}, u'author': u'张仲景'} 
            
    def __is_start_section__(self, line):
        #second section: u'\u7b2c\u4e8c'
        matches = re.findall(ur"\u7b2c\u4e8c", line)
        return len(matches) > 0;
    
    def __is_last_section__(self, line):
        #twenty three section: u'\u7b2c\u4e8c\u5341\u4e09'
        matches = re.findall(ur"\u7b2c\u4e8c\u5341\u4e09", line)
        return len(matches) > 0;
    
    def __create_clause__(self, item_contents, category):
        content = '\n'.join(item_contents)
        matches = re.findall(ur"\s*(\d{1,3})\u3001", content)
        index = int(matches[0])
        clause = {'index':index, 'content' : content, 'category':category}        
        clause.update(self._source)
        parser = PrescriptionParser(content, "方：") 
        parser.get_prescriptions()      
        return clause
    
    def get_all_clauses(self):
        clauses = []     
        jkyl = codecs.open(self._source_file_fullpath, 'r', 'utf-8')  
        current_sec = None
        item_contents = []
        
        importing = False
        for line in jkyl:
            if self.__is_last_section__(line):
                break
            if not importing:
                if self.__is_start_section__(line):
                    importing = True
                else:
                    continue
                
            # Parse section
            if len(re.findall(ur"\u7b2c", line)) > 0:
                if current_sec:
                    clauses.append(self.__create_clause__(item_contents, current_sec))
                    item_contents = []
                current_sec = line
                continue
            # Parse Tiaowen
            matches = re.findall(ur"\s*\d{1,3}\u3001", line)
            if len(matches) > 0:
                if len(item_contents) > 0:
                    clauses.append(self.__create_clause__(item_contents, current_sec))
                    item_contents = []
            if len(line.strip()) > 0:
                item_contents.append(line.strip())             
        return clauses

if __name__ == "__main__":
    provider = GoldenChamberProvider()
    clauses = provider.get_all_clauses()
    #print clauses
    print "done"