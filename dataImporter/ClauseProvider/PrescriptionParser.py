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

from ComponentAdjustor import *
from dataImporter.Utils.Utility import *

#TBD
class SingleComponentParser_jf:
    def __init__(self, text):
        self._source_text = text
        self._herb = text
        self._quantity_unit = None
        self._comments = None 
        
    def __parse_quantity_comment__(self, text):
        quantity_unit_pattern = ur"([一二三四五六七八九十半百]+[^，]+)"
        successed = False
        # quantity（comment）
        m = re.compile(quantity_unit_pattern + ur"[^（）]*（([^（）]+)）").match(text)
        if m:
            self._quantity_unit = m.group(1).strip()
            self._comments = m.group(2).strip()
            successed = True
            
        if not successed:#（comment）quantity
            m = re.compile(ur"（([^（）]+)）" + quantity_unit_pattern).match(text)
            if m:
                self._quantity_unit = m.group(2).strip()
                self._comments = m.group(1).strip()
                successed = True
                
        if not successed:#quantity
            m = re.compile(quantity_unit_pattern).match(text)
            if m:
                successed = True
                self._quantity_unit = m.group(1).strip()
                successed = True
                
        if not successed:#comment
            self._comments = text.strip()
    
    def __parse_normal_medical_name__(self):
        pattern = ur"([^（）一二三四五六七八九十半百]+)(\W*（[^（）]+）\W*)"
        m = re.compile(pattern).match(self._source_text)
        if m:
            self._herb = m.group(1).strip()
            self.__parse_quantity_comment__(m.group(2).strip())

    def get_component(self):   
        m = MedicalNameParser(self._source_text)
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
    
class PrescriptionParser:
    def __init__(self, text, prescription_name_end_tag):
        self._source_text = text  
        self._prescription_name_end_tag = prescription_name_end_tag       
        
    def __get_name__(self, text, appendix_content):
        '''
        Line ends with 方 (\u65b9)
        '''
        name = None
        if not appendix_content: #桂枝芍药知母汤方 
            pattern = ur"(\W*)" + self._prescription_name_end_tag + ur"$"
            matches = re.findall(pattern, text)
            if len(matches) > 0:
                name = matches[0]
        if not name:
            possible_key_words = []
            if appendix_content:  #牡蛎汤：治牡疟。              
                possible_key_words.append(u'汤方：')
                possible_key_words.append(u'汤：')
                possible_key_words.append(u'丸：')
                possible_key_words.append(u'散：')
                possible_key_words.append(u'饮：')
            else:    #乌头汤方：治脚气疼痛，不可屈伸。
                possible_key_words.append(u'汤方：')
                possible_key_words.append(u'丸方：')
                possible_key_words.append(u'散方：')
                possible_key_words.append(u'酒方：')        
                
            for key_word in possible_key_words:
                matches = re.findall(ur'(\W+)'+key_word, text)
                if len(matches) > 0:
                    name = matches[0] + key_word[0]
                    break               
        return name
    
    def __parse_components__(self, text):
        '''
        Should not include Chinese period (\u3002)
        '''
        if text.find(u'\u3002') >=0:
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
                component_parser = SingleComponentParser_jf(item)
                components.append(component_parser.get_component())

        #防风　桔梗　桂枝　人参　甘草各一两
        components.reverse()
        previous_quantity = None
        previous_unit = None
        for component in components:#{'quantity': quantity, 'medical': medical, 'unit': unit, 'comments': comments}
            medical_name = component['medical']
            if medical_name[-1] == "各":
                previous_quantity = component['quantity']
                previous_unit = component['unit']
                component['medical'] = medical_name[:len(medical_name)-1]
            else:
                if not component['unit'] or len(component['unit'])== 0: 
                    if not previous_unit > 0:
                        component['quantity'] = previous_quantity
                        component['unit'] = previous_unit
                else:
                    previous_quantity = None
                    previous_unit = None             
            
        components.reverse()
        
        if (len(components) == 0):
            print "*failed to get components from: " + text + '\n'
        return components
        
    def get_prescriptions(self):
        prescriptions = []# name, detail, composition, source    
        
        matches = re.findall(ur"\s*\n+(\W*\u65b9\s*\W*)", self._source_text, re.M) #u65b9:方
        if len(matches) > 0:
            prescription_text = matches[0].strip()
            
            prescription_contents = filter(lambda x: len(x) > 0, [item.strip() for item in prescription_text.split('\n')])
            
            appendix_content = False 
 
            current_prescription = None      
            for item in prescription_contents:  # One clause may include multiple prescriptions
                if not item.startswith(u'附子') and len(re.findall(u"^附(\W*)方$", item, re.M)) > 0:
                    appendix_content = True
                    continue
                
                name = self.__get_name__(item, appendix_content)
                if name:   
                    if current_prescription and len(current_prescription['components'])>0:                  
                        prescriptions.append(current_prescription)                        
                    current_prescription = {'name':name, 'components':[]}               
                    continue
                components = self.__parse_components__(item)
                if components:
                    current_prescription['components'].extend(components)
                    continue
                
                if current_prescription:
                    current_prescription['comment'] = item
                    
            if current_prescription and len(current_prescription['components']) > 0:
                prescriptions.append(current_prescription)    
        return prescriptions
    
    
def print_prescription(prescription): 
    print "name: " + prescription['name']
    print "components:"  
    for component in prescription['components']:
        Utility.convert_dict_to_string(component)
    print "comment: " + prescription['comment']  
    
def print_prescription_list(prescriptions):
    for item in prescriptions:
        print_prescription(item)
        print ""
    
if __name__ == "__main__": 
    parser = PrescriptionParser('', u'方：')
    print parser.__get_name__(u'《千金》麻黄醇酒汤：', True)
    parser.__parse_components__(u'桂枝一两十七铢（去皮）　芍药一两六铢　麻黄十六铢（去节）　生姜一两六铢（切）　杏仁十六个（去皮尖）　甘草一两二铢（炙）　大枣五枚（擘）')
    texts = [u'甘草（炙）各十八铢',
             u'庶（虫底）虫半升',
             u'庶（虫底）虫二十枚',
             u'庶（虫底）虫二十枚（熬，去足）',
             u'栝蒌根各等分', 
             u'半夏一分', 
             u'五味子', 
             u'蜀椒三分（去汗）', 
             u'蜀椒（去汗）三分', 
             u'蜀椒', 
             u'蜀椒（去汗）', 
             u'蜀椒（去汗）等分', 
             u'蜀椒三分', 
             u'蜀椒百分',
             u'蜀椒三分半']     
    
    for item in texts:
        print item + " "
        sp = SingleComponentParser_jf(item)
        component = sp.get_component()
        print Utility.convert_dict_to_string(component)
        
        
        
