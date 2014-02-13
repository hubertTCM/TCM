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
        self._source_text = text
        self._medical_names_contains_number = [] 
        self._medical_names_contains_number.append(u'半夏') 
        self._medical_names_contains_number.append(u'五味子')   
        self._medical_names_contains_number.append(u'五味')  
        
    def __adjust_quantity_unit__(self, quantity, unit):
        if (len(quantity) > 0):
            quantity = Utility.convert_number(quantity)
        if len(unit) > 0 and unit[-1] == "半": #生姜一两半
            unit = unit[0:len(unit) - 1]
            quantity += 0.5
        return quantity, unit
    
    def __parse_quantity_unit__(self, item):
        quantity = ''
        unit = ''
        matches = re.findall(ur"[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u96f6\u5341\u534a]{1,3}", item) #one to ten
        if (len(matches) > 0): 
            quantity = matches[0]
            unit = item[item.rindex(quantity) + len(quantity):]                                
            quantity, unit = self.__adjust_quantity_unit__(quantity, unit)                            
        return quantity, unit

    def __parse_medical_quantity_unit__(self, item):
        medical = item
        quantity = ''
        unit = ''
        
        for name in self._medical_names_contains_number:
            if item.startswith(name):
                medical = name
                quantity, unit = self.__parse_quantity_unit__(item[len(name):])
                return medical, quantity, unit
        
        matches = re.findall(ur"[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u96f6\u5341\u534a]{1,3}", item) #one to ten
        if len(matches) > 0: #format: 蜀椒三分
            quantity = matches[0]
            medical = item[0:item.rindex(quantity)]
            unit = item[item.rindex(quantity) + len(quantity):]                        
            quantity, unit = self.__adjust_quantity_unit__(quantity, unit)          
            
        return medical, quantity, unit

    def get_component(self):        
        ''' format:
                    蜀椒三分（去汗）
                    蜀椒（去汗）三分
                    蜀椒
                    蜀椒（去汗）
                     蜀椒（去汗）等分           
                    蜀椒三分
        '''
        quantity = ''
        medical = ''
        unit = ''
        comments = ''
        
        #print 'get_component ' +  self._source_text
        
        items = re.split(ur"\uff08(\W+)\uff09", self._source_text.strip())       
        items = [item.strip() for item in items if len(item.strip()) > 0]
        
        if (len(items) == 1): #蜀椒  or 蜀椒三分
            item = items[0]
            medical = items[0]
            medical, quantity, unit = self.__parse_medical_quantity_unit__(item)
            
        if (len(items) == 2): #蜀椒三分（去汗） or 蜀椒（去汗）
            item = items[0]
            medical = item
            medical, quantity, unit = self.__parse_medical_quantity_unit__(item)
            comments = items[1]
            
        if (len(items) == 3): #蜀椒（去汗）三分 or 牡蛎（熬）等分
            medical = items[0]
            comments = items[1]
            item = items[2]
            quantity, unit = self.__parse_quantity_unit__(item)
        
        #print ' [' + self._source_text + ']  medical： ' + medical + '  quantity： ' + str(quantity) + '  unit： ' + unit + '  comments： ' + comments
        return {'quantity': quantity, 'medical': medical, 'unit': unit, 'comments': comments}
      
class PrescriptionParser:
    def __init__(self, text, prescription_name_end_tag):
        self._source_text = text  
        self._prescription_name_end_tag = prescription_name_end_tag       
        
    def __parse_name__(self, text):
        '''
        Line ends with 方 (\u65b9)
        '''
        name = None
        # For SHL
        #matches = re.findall(ur"(\W*)\u65b9$", text)
        # For JKYL
        #matches = re.findall(ur"(\W*)\u65b9\uff1a$", text)
        pattern = ur"(\W*)" + self._prescription_name_end_tag + ur"$"
        matches = re.findall(pattern, text)
        if len(matches) > 0:
            name = matches[0]
        return name
    
    def __parse_components__(self, text):
        '''
        Should not include Chinese period (\u3002)
        '''
        items = [item.strip() for item in text.split(u'\u3000')] #\u3000' is blank space
        if text.find(u'\u3002') >=0 or len(items) <= 0:
            print "*** none item for " + text + '\n'
            return None
        components = []
        for item in items:
            item = item.strip()
            if len(item) > 0:
                component_parser = SingleComponentParser(item)
                components.append(component_parser.get_component())

        ''' special case:
                        防风　桔梗　桂枝　人参　甘草各一两
        '''
        components.reverse()
        previous_quantity = ''
        previous_unit = ''
        for component in components:#{'quantity': quantity, 'medical': medical, 'unit': unit, 'comments': comments}
            medical_name = component['medical']
            if medical_name[-1] == "各":
                previous_quantity = component['quantity']
                previous_unit = component['unit']
                component['medical'] = medical_name[:len(medical_name)-1]
            else:
                if len(component['unit'])== 0: 
                    if (previous_unit) > 0:
                        component['quantity'] = previous_quantity
                        component['unit'] = previous_unit
                else:
                    previous_quantity = ''
                    previous_unit = '' 
            
            
            Utility.print_dict(component)                          
        return components
        
    def get_prescriptions(self):
        prescriptions = []# name, detail, composition, source    
        
        '''
        Parse each clause to generate prescription
        '''
        matches = re.findall(ur"\s*\n+(\W*\u65b9\s*\W*)", self._source_text, re.M)
        if len(matches) > 0:
            prescription_text = matches[0].strip()
            print "prescription_text: " + prescription_text + "**"
            
            prescription_contents = filter(lambda x: len(x) > 0 , [item.strip() for item in prescription_text.split('\n')])
            # One clause may include multiple prescriptions
            for item in prescription_contents:
                name = self.__parse_name__(item)
                if name:   
                    prescription = {'name': name, 'components' : None, 'content' : ''}                  
                    prescriptions.append(prescription)
                    continue
                components = self.__parse_components__(item)
                if components and len(prescriptions) > 0:
                    prescriptions[-1]['components'] = components
                    continue
        return prescriptions
    
if __name__ == "__main__":
    texts = [u'半夏一分', u'五味子', u'蜀椒三分（去汗）', u'蜀椒（去汗）三分', u'蜀椒', u'蜀椒（去汗）', u'蜀椒（去汗）等分', u'蜀椒三分', u'蜀椒三分半']
    for item in texts:
        print item + " "
        sp = SingleComponentParser(item)
        component = sp.get_component()
        Utility.print_dict(component)
        print " "
        
        
