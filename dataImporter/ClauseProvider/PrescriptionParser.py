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

class AdjustorCollection:
    def __init__(self):
        self._adjustors = []
        
    def append(self, adjustor):
        self._adjustors.append(adjustor)
        
    def adjust(self, item):
        value = item
        for adjustor in self._adjustors:
            value = adjustor.adjust(value)
        return value
            
class HerbNameAdjustor_jf:
    def __init__(self):
        self._end_tags = []
        self._end_tags.append(u"手指大")
        self._end_tags.append(u"如弹丸大")
        self._end_tags.append(u"如指大")
        self._end_tags.append(u"大者")
        self._end_tags.append(u"鸡子大")
        self._end_tags.append(u"如鸡子大")
        self._end_tags.append(u"弹丸大")
        self._end_tags.append(u"等分")
        self._end_tags.append(u"少许")
        
        self._end_tags.sort(key=lambda x: len(x), reverse=True) 
        
    def adjust(self, herb):
        for item in self._end_tags:
            if herb.endswith(item):
                return herb[:len(herb)-len(item)]
        return herb

class HerbNameMap_jf:
    def __init__(self):
        self._map = {u"瓜子":u"冬瓜子",
                     u"瓜瓣":u"冬瓜子",
                     u"生葛":u"葛根",
                     u"食蜜":u"蜂蜜",
                     u"蜜":u"蜂蜜",
                     u"太一禹余粮":u"禹余粮"
                     }
    def adjust(self, herb):
        if herb in self._map:
            return self._map[herb]
        return herb
        
class ComponentAdjustor_jf:
    def __init__(self, herb_adjustor):        
        self._herb_adjustor = herb_adjustor
        
    def adjust(self, component):
        herb = component['medical']
        component['medical'] = self._herb_adjustor.adjust(herb)
        return component

class SingleComponentParser_jf:
    def __init__(self, text, component_adjustor):
        self._source_text = text
        self._herb = text
        self._quantity_unit = None
        self._apply_quantity_to_others = False
        self._comments = None 
        self._component_adjustor = component_adjustor
        
    def __parse_quantity_comment__(self, text):
        quantity_unit_pattern = ur"([一二三四五六七八九十半百]+[^（(]+)"
        comment_pattern = ur"[（(]([\W]+)[)）]"
        successed = False
        # quantity（comment）
        m = re.compile(quantity_unit_pattern + comment_pattern).match(text)
        if m:
            self._quantity_unit = m.group(1).strip()
            self._comments = m.group(2).strip()
            successed = True
            
        if not successed:#（comment）quantity
            m = re.compile(comment_pattern + ur"([各]*)" + quantity_unit_pattern).match(text)
            if m:
                self._quantity_unit = m.group(3).strip()
                self._comments = m.group(1).strip()
                if len(m.group(2)) > 0:
                    self._apply_quantity_to_others = True
                    
                successed = True
                
        if not successed:#quantity
            m = re.compile(quantity_unit_pattern).match(text)
            if m:
                successed = True
                self._quantity_unit = m.group(1).strip()
                successed = True
                
        if not successed:#comment
            m = re.compile(comment_pattern).match(text)
            if m:
                self._comments = m.group(1).strip()
    
    def __parse_normal_medical_name__(self):
        pattern = ur"([^（）一二三四五六七八九十半百各]+)(\W*)"
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
         
        component = {'medical': self._herb, 'quantity': quantity, 'unit': unit, 'comments': self._comments, 
                     "applyQuantityToOthers":self._apply_quantity_to_others} 
        
        if self._component_adjustor:
            component = self._component_adjustor.adjust(component)
        
        return component
    
class PrescriptionParser:
    def __init__(self, text, prescription_name_end_tag, components_adjustor):
        self._source_text = text  
        self._prescription_name_end_tag = prescription_name_end_tag   
        self._components_adjustor = components_adjustor    
        
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
        not_components = []
        not_components.append(u"土瓜根方（附方佚）")
        not_components.append(u"猪胆汁方（附方）")
        for item in not_components:
            if text.startswith(item):
                return None
        
        items = []
        for item in [item.strip() for item in text.split(u'\u3000')]: #\u3000' is blank space:
            items.extend(filter(lambda(x): len(x) > 0, [temp_item.strip() for temp_item in item.split(' ')]))           
        if len(items) <= 0:
            return None
        
        components = []
        
        herb_adjustor = AdjustorCollection()
        herb_adjustor.append(HerbNameAdjustor_jf())
        herb_adjustor.append(HerbNameMap_jf())
        
        component_adjustor = ComponentAdjustor_jf(herb_adjustor)
        
        for item in items:
            item = item.strip()
            if len(item) > 0:
                component_parser = SingleComponentParser_jf(item, component_adjustor)
                components.append(component_parser.get_component())
                
        if self._components_adjustor:        
            components = self._components_adjustor.adjust(components)
        
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
    parser = PrescriptionParser('', u'方：', QuantityAdjustor())
    print parser.__get_name__(u'《千金》麻黄醇酒汤：', True)
    components = parser.__parse_components__(u'甘草（炙）各四两')
    for component in components:
        print Utility.convert_dict_to_string(component)
        
    
    herb_adjustor = AdjustorCollection()
    herb_adjustor.append(HerbNameAdjustor_jf())
    herb_adjustor.append(HerbNameMap_jf())
        
    texts = [u'川乌五枚（父（口旁）咀，以蜜二升，煎取一升，即出乌头）',
             u'甘草（炙）各十八铢',
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
        sp = SingleComponentParser_jf(item, ComponentAdjustor_jf(herb_adjustor))
        component = sp.get_component()
        print Utility.convert_dict_to_string(component)
        
        
        
