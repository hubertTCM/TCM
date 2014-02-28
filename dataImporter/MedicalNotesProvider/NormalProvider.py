# -*- coding: utf-8 -*-
'''
Module to read 'jsya.txt' to generate YiAn of Yi Jusun
'''
import sys
import os
import codecs
import re


def append_ancestors_to_system_path(levels):
    parent = os.path.dirname(__file__)
    for i in range(levels):
        sys.path.append(parent)
        parent = os.path.abspath(os.path.join(parent, ".."))
        
append_ancestors_to_system_path(3)

from dataImporter.Utils.Utility import *


class MedicalNoteProvider:
    def __init__(self):
        self._file_names =[]
        self._file_names.append(('jsya.txt',ur"\u3001"))
        self._file_names.append(('zyhyl.txt',ur"\uff0e"))
        
    def get_all(self):    
        notes = []
        for file_name, split_word in self._file_names:
            source_file = codecs.open(file_name, 'r', 'utf-8', 'ignore')
            file_content = source_file.read()
            source_file.close()
            matches = re.findall(ur"(\d{1,3}"+split_word+".+)", file_content, re.M)
            for i in range(len(matches)):
                itemstart = matches[i]
                if i == len(matches) - 1:
                    '''last item'''
                    item = file_content[file_content.index(itemstart):]
                else:
                    item = file_content[file_content.index(itemstart):file_content.index(matches[i+1])]
                item = item.strip()
                title = itemstart.split(split_word)[1].strip()
                content = item[len(itemstart):].strip()
                notes.append({'title':title, 'content':content})
                
                
        return notes
    
    
    
if __name__ == "__main__":
    p = MedicalNoteProvider()
    for note in p.get_all():
        Utility.print_dict(note)