# -*- coding: utf-8 -*-
import codecs
import fnmatch
import os
import re
import sys

from ComponentAdjustor import *

def append_ancestors_to_system_path(levels):
    parent = os.path.dirname(__file__)
    for i in range(levels):
        sys.path.append(parent)
        parent = os.path.abspath(os.path.join(parent, ".."))
        
append_ancestors_to_system_path(3)

from dataImporter.Utils.Utility import *
from dataImporter.Utils.WebUtil import *

class SingleComponentParser_wbtb:
    '''
            鸡子黄（生用，一枚）
            鸡子黄（一枚，生用）
            鸡子黄（一枚）
            鸡子黄（一枚）
            鸡子黄
    '''
    def __init__(self, text):
        self._source_text = text#.replace(ur'\u3000',' ').strip()
        self._herb = text
        self._quantity_unit = None
        self._comments = None
        
        
    def __parse_quantity_comment__(self, text):   
        quantity_unit_pattern = ur"([一二三四五六七八九十半百]+[^，])"
        successed = False
        # （quantity, comment）
        m = re.compile(ur"（" + quantity_unit_pattern + ur"[，]([^（）]+)）").match(text)
        if m:
            self._quantity_unit = m.group(1).strip()
            self._comments = m.group(2)
            successed = True
            
        if not successed:#(comment,quantity)
            m = re.compile(ur"（([^（）]+)[，]" + quantity_unit_pattern + ur"）").match(text)
            if m:                
                self._quantity_unit = m.group(1)
                self._comments = m.group(2)
                successed = True
        
        if not successed:#(quantity)
            m = re.compile(ur"（" + quantity_unit_pattern + ur"）").match(text)
            if m:
                successed = True
                self._quantity_unit = m.group(1)
                successed = True
        if not successed:#(comment)
            m = re.compile(ur"（(\W+)）").match(text)
            if m:
                successed = True
                self._comments = m.group(1)
                successed = True
         
    def __parse_normal_medical_name__(self):      
        pattern = ur"([^（）]+)(（\W+）)"       
        m = re.compile(pattern).match(self._source_text)
        if m: #medical(other)
            self._herb = m.group(1).strip()
            self.__parse_quantity_comment__(m.group(2))
            
    def get_component(self):   
        m = MedicalNameAdjustor(self._source_text)
        herb, other = m.split_with_medical_name()
        if herb:
            self._herb = herb
            self.__parse_quantity_comment__(other)
        else:
            self.__parse_normal_medical_name__()
        
        quantity, unit = (None, None)
        if self._quantity_unit:
            quantity_parser = QuantityParser(self._quantity_unit)
            quantity, unit = quantity_parser.parse()
         
        return {'medical': self._herb, 'quantity': quantity, 'unit': unit, 'comments': self._comments} 
        #return {'medical':self._herb, 'comment':self._comment, 'quantity_unit':self._quantity_unit}  
    

class PrescriptionParser_wbtb:
    def __init__(self, clause_lines):
        self._clause_lines = clause_lines  
        self._adjustor = ComponentsAdjustor() 
        
    def __is_component_info__(self, text):
        #水八杯，先煮
        if text.find(u"。") >=0 and text.find("（") < 0:
            return False
        exclude_patterns = [
                            ur"[^（）]*水[一二三四五六七八九十半百]+[杯升]"
                            ]
        for pattern in exclude_patterns:
            m = re.findall(pattern, text)
            if len(m) >0:
                print m[0]
                return False
        return True       
        
    def __parse_components__(self, text):
        text = text.replace(ur'\u3000',' ').strip()
        if not self.__is_component_info__(text):
            return None
                
        items = []
        for item in [item.strip() for item in text.split(u'\u3000')]: #\u3000' is blank space:
            items.extend(filter(lambda(x): len(x) > 0, [temp_item.strip() for temp_item in item.split(' ')]))           
        if len(items) <= 0:
            return None
        
        components = []
        for item in items:
            item = item.strip()
            if len(item) > 0:
                component_parser = SingleComponentParser_wbtb(item)
                component = component_parser.get_component()
                components.append(component)
                
                print Utility.convert_dict_to_string(component)

        #components = self._adjustor.adjust(components)
        
        if (len(components) == 0):
            print "*failed to get components from: " + text + '\n'
            return None
        
        return components
    
    def __get_name__(self, text):
        name_pattern = ur"(\W+)方$"
        matches = re.findall(name_pattern, text)
        if len(matches)==1:
            return matches[0]
        return None
        
    def __get_name_info__(self, text):    
        method = None         
        method_pattern = ur"[\uff08(](\W+)[)\uff09]$"#check ( in both of Chinese and English.
        items = filter(lambda(x):len(x)>0, [item.strip() for item in re.split(method_pattern, text)])
                
        name = self.__get_name__(items[0])
        if len(items)==2:
            method = items[1]
            if method[-1] == u"法":
                method = method[:-1]
        
        if not name:
            return {}
        
        info = {'name':name, 'method':method}
        print "**" + Utility.convert_dict_to_string(info)
        return info
        
    def get_prescriptions(self):
        prescriptions = []# name, detail, components, source
        
        current_prescription = None    
        for line in self._clause_lines:
            info = self.__get_name_info__(line)
            if info:   
                if current_prescription and len(current_prescription['components'])>0:                  
                    prescriptions.append(current_prescription)                        
                current_prescription = {'components':[]}  
                current_prescription.update(info)             
                continue
            
            if not current_prescription:
                continue
            
            components = self.__parse_components__(line)
            if components:
                current_prescription['components'].extend(components)
                continue
            
            if current_prescription:
                current_prescription['comment'] = line
                    
        if current_prescription and len(current_prescription['components']) > 0:
            prescriptions.append(current_prescription) 
  
        return prescriptions

class wbtb_provider:
    def __init__(self, source_folder):
        if not source_folder:
            source_folder = os.path.dirname(__file__)
            source_folder = os.path.join(source_folder, 'wbtb')
            
        self._come_from = {u'category': u'Book', u'name': u'温病条辩'} 
        index_file_name = os.path.join(source_folder, "index_source.txt")
        self._source_file_names = []
        index_file = codecs.open(index_file_name, 'r', 'utf-8', 'ignore')
        for line in index_file:
            try:
                value = Utility.get_dict_from(line.strip())
                self._source_file_names.append(os.path.join(source_folder, value['name'].strip()+".txt"))          
            except Exception,ex:
                print Exception,":",ex, "***" + line

        index_file.close()

    def __create_caluse__(self, index, item_contents):
        items = [item.strip() for item in item_contents if len(item.strip()) > 0]
        content = ''
        if len(items) > 0:
            content = '\n'.join(items)
        items = content.split('\n')     
        parser = PrescriptionParser_wbtb(items) 
        prescriptions = parser.get_prescriptions() 
        for prescription in prescriptions:
            prescription.update({'comeFrom' : self._come_from})          
            
        return {'index':index, 'content':content, 'prescriptions':prescriptions, 'comeFrom' : self._come_from}
    
    def __is_start_line_of_clause__(self, line):
        #matches = re.findall(ur"\s*[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u96f6]{1,3}\u3001", line)
        matches = re.findall(ur"\s*[一二三四五六七八九十百]{1,3}\u3001", line)
        return len(matches) > 0 and line.strip().index(u'\u3001') < 4
        
    def __get_clauses_from__(self, file_name): 
        clauses = []
        print file_name
        source_file = codecs.open(file_name, 'r', 'utf-8')
        clause_lines = []
        index = 0
        for line in source_file:
            if self.__is_start_line_of_clause__(line):
                if (len(clause_lines) > 0):
                    clauses.append(self.__create_caluse__(index, clause_lines))
                index += 1
                clause_lines = []                
                clause_lines.append(line.strip())
            else:    
                clause_lines.append(line.strip())
                
        source_file.close
        
        if len(clause_lines) > 0:
            clauses.append(self.__create_caluse__(index, clause_lines))
        
        return clauses
            
    def get_all_clauses(self):
        clauses = []
        for file_name in self._source_file_names:
            items = self.__get_clauses_from__(file_name)
            if len(items) > 0:
                clauses.extend(items)
        return clauses
                
if __name__ == "__main__":
    source_folder = os.path.dirname(__file__)
    source_folder = os.path.join(source_folder, 'wbtb')   
    provider = wbtb_provider(source_folder)
    provider.get_all_clauses()
    
#     items = [
#             u"鸡子黄（生用，一枚）",
#             u"鸡子黄（一枚，生用）",
#             u"鸡子黄（一枚）",
#             u"鸡子黄（生用）",
#             u"鸡子黄",
#             u"百合（生用，一枚）",
#             u"百合"
#             ]
#     #pattern = ur"([^（）]+)（([^（）]+)）"
#     quantity_pattern = ur"([一二三四五六七八九十百]+\W+)" 
#     pattern = ur"([^（）]+)（" + quantity_pattern + ur"[，]([^（）]+)"
#     
#     p = re.compile(pattern)
#     for item in items:
#         print item
#         m = p.match(item)
#         if m:
#             print "        ==         ", m.group(1), " 0  ", m.group(2), " 0  ", m.group(3)
#         else:
#             print item, "%"
    print "done"