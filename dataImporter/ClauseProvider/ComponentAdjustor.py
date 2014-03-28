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
class MedicalNameParser: 
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
        self._medical_names.append(u'京三棱')
        self._medical_names.append(u'庶（虫底）虫')
        self._medical_names.append(u'太一禹余粮')
        
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

class QuantityParser:
    def __init__(self, text):
        self._source_text = text.strip()
        self._unit = None
        self._quantity = None
        
    def __adjust__(self):
        pass
    
    def parse(self):
        m = re.findall(ur"[一二三四五六七八九十半百]+", self._source_text)
        pairs = [] 
        if m:
            start_index = 0
            current_unit = None
            current_quantity = None
            for i in range(len(m)):
                index = self._source_text.index(m[i], start_index)
                if start_index > 0:
                    current_unit = self._source_text[start_index:index]
                    pairs.append((current_quantity, current_unit))
                current_quantity = m[i]
                start_index = index + len(m[i])
            pairs.append((current_quantity, self._source_text[start_index:]))
        
        #TBD, need update here to convert UOM
        if len(pairs) == 1:
            str_quantity, self._unit = pairs[0]
            self._quantity = Utility.convert_number(str_quantity)
        if len(pairs) == 2:
            str_quantity, self._unit = pairs[0]
            if (not pairs[1][1] or len(pairs[1][1]) == 0 ) and pairs[1][0] == u'半':
                self._quantity = Utility.convert_number(str_quantity)
                self._quantity += 0.5
            
        
        return self._quantity, self._unit       
     
class QuantityAdjustor:    
    def adjust(self, components):
        components.reverse() #防风　桔梗　桂枝　人参　甘草各一两
        previous_quantity = None
        previous_unit = None
        for component in components:#{'quantity': quantity, 'medical': medical, 'unit': unit, 'comments': comments}
            apply_quantity_to_others = Utility.get_bool_value('applyQuantityToOthers', component)
            if apply_quantity_to_others:
                previous_quantity = component['quantity']
                previous_unit = component['unit']
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
    
if __name__ == "__main__":
    items = [
              u"一一二枚",
              u"一二钱五分",
              u"三分半"
             ]
    for item in items:
        p =QuantityParser(item)
        pairs = p.parse()
        print pairs