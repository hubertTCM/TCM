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

from dataImporter.Utils.Utility import *

class SingleComponentParser:
    def __init__(self, text):
        self._source_text = text.replace(ur'\u3000',' ').strip()
        
        self._known_medical = [] 
        self._known_medical.append(u'百合')
        self._known_medical.append(u'半夏') 
        self._known_medical.append(u'五味子')   
        self._known_medical.append(u'五味')  
        self._known_medical.append(u'庶（虫底）虫')
        
        #self._comment_pattern = ur"\uff08(\W+)\uff09"
        self._comment_pattern = ur"[\uff08(](\W+)[)\uff09]" #check ( in both of Chinese and English.  
    
    def __adjust_medical_name__(self, medical_name):
        text_should_remove = []
        text_should_remove.append(u'各等分')
        text_should_remove.append(u'等分')
        for item in text_should_remove:
            if medical_name.endswith(item):
                return medical_name[:len(medical_name)-len(item)].strip()      
         
        return medical_name.strip()
    
    def __split_with_comment_tag__(self, text):
        return filter(lambda(x):len(x)>0, [item.strip() for item in re.split(self._comment_pattern, text)])
    
    def __adjust_quantity__(self, quantity):
        if not quantity or len(str(quantity).strip()) == 0:
            return None              
            
        return quantity
    
    def __adjst_unit__(self, unit):
        if not unit or len(str(unit).strip()) == 0:
            return None  

        if len(self.__split_with_comment_tag__(unit)) > 1:
            return None 
        
        quantity_pattern = u"[一二三四五六七八九十百]"
        if len(re.split(quantity_pattern, unit)) > 1:            
            return None
        return unit
            
    def __adjust_quantity_unit__(self, quantity, unit):
        if len(quantity) > 0:
            quantity = Utility.convert_number(quantity)
            
        if len(unit) > 0 and unit[-1] == "半": #生姜一两半
            unit = unit[0:len(unit) - 1]
            quantity += 0.5
                            
        return self.__adjust_quantity__(quantity), self.__adjst_unit__(unit)
    
    def __find_quantity__(self, item):
        quantity_pattern =  ur"[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u96f6\u5341\u534a\百]{1,3}"
        return re.findall(quantity_pattern, item)

    def __parse_quantity_unit__(self, item):
        quantity = None
        unit = None
        matches = self.__find_quantity__(item)
        if (len(matches) > 0): 
            quantity = matches[0]
            unit = item[item.rindex(quantity) + len(quantity):]                                
            quantity, unit = self.__adjust_quantity_unit__(quantity, unit)                            
        return quantity, unit

    def __parse_medical_quantity_unit__(self, item):
        medical = item
        quantity = None
        unit = None        
        matches = self.__find_quantity__(item)
        if len(matches) > 0: #format: 蜀椒三分
            quantity = matches[0]            
            medical = item[0:item.rindex(quantity)].strip()            
            unit = item[item.rindex(quantity) + len(quantity):]                        
            quantity, unit = self.__adjust_quantity_unit__(quantity, unit)          
            
        return medical, quantity, unit

    def get_component(self): 
        medical = ''       
        quantity = None
        unit = None
        comments = ''
        
        #comment_pattern = ur"\uff08(\W+)\uff09"
            
        for name in self._known_medical: #庶（虫底）虫二十枚（熬，去足）
            if self._source_text.startswith(name):
                medical = name
                items =self.__split_with_comment_tag__(self._source_text[len(name):])#filter(lambda(x):len(x)>0, [item.strip() for item in re.split(comment_pattern, self._source_text[len(name):])])
                if (len(items)==2):
                    comments = items[1]
                if len(items) > 0:    
                    quantity, unit = self.__parse_quantity_unit__(items[0])                    
                return {'quantity': quantity, 'medical': medical, 'unit': unit, 'comments': comments}
                
        #items =filter(lambda(x):len(x)>0, [item.strip() for item in re.split(comment_pattern, self._source_text)])
        items =self.__split_with_comment_tag__(self._source_text)
        if (len(items) == 1): #蜀椒  or 蜀椒三分
            item = items[0]
            medical, quantity, unit = self.__parse_medical_quantity_unit__(item)
            
        if (len(items) == 2): #蜀椒三分（去汗） or 蜀椒（去汗）
            item = items[0]
            comments = items[1]
            medical, quantity, unit = self.__parse_medical_quantity_unit__(item)
            
        if (len(items) == 3): #蜀椒（去汗）三分 or 牡蛎（熬）等分
            medical = items[0]
            comments = items[1]
            item = items[2]
            quantity, unit = self.__parse_quantity_unit__(item)        
        
        medical = self.__adjust_medical_name__(medical)
        
        return {'quantity': quantity, 'medical': medical, 'unit': unit, 'comments': comments}
      
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
                component_parser = SingleComponentParser(item)
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
        
        matches = re.findall(ur"\s*\n+(\W*\u65b9\s*\W*)", self._source_text, re.M)
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
        Utility.print_dict(component)
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
             u'蜀椒三分半']     
    
    for item in texts:
        print item + " "
        sp = SingleComponentParser(item)
        component = sp.get_component()
        Utility.print_dict(component)
        
        
        
