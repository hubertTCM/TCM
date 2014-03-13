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


#TBD
class MedicalNameAdjustor: 
    # special medical names, like medical name with quantity
    def __init__(self, text):
        self._source_text = text
        self._medical_name = text
        
        self._medical_names = [] 
        self._medical_names.append(u'百合')
        self._medical_names.append(u'半夏') 
        self._medical_names.append(u'五味子')   
        self._medical_names.append(u'五味')  
        self._medical_names.append(u'五灵脂')
        self._medical_names.append(u'三棱')
        self._medical_names.append(u'京 三棱')
        self._medical_names.append(u'庶（虫底）虫')
        
    def split_with_medical_name(self):
        medical_name = None
        other_part = self._source_text
        
        for name in self._medical_names: #庶（虫底）虫二十枚（熬，去足）
            if self._source_text.startswith(name):
                medical_name = name
                other_part = self._source_text[len(name):]
                self._medical_name = name
                break
            
        return medical_name, other_part
       
    def adjust(self):
        text_should_remove = []
        text_should_remove.append(u'各等分')
        text_should_remove.append(u'等分')
        for item in text_should_remove:
            if self._medical_name.endswith(item):
                self._medical_name = self._medical_name[:len(self._medical_name)-len(item)]
                break
        
        return self._medical_name   


class QuantityAdjustor:
    def __init__(self, quantity, unit):
        pass
    
    def adjust(self):
        pass
     
class ComponentsAdjustor:    
    def adjust(self, components):
        components.reverse() #防风　桔梗　桂枝　人参　甘草各一两
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
        return components
    