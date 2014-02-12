# -*- coding: utf-8 -*-
import re

class SingleComponentParser:
    def __init__(self, text):
        self._source_text = text
    
    def get_component(self):        
        ''' format:
                    蜀椒三分（去汗）
                    蜀椒（去汗）三分
                    蜀椒
                    蜀椒（去汗）
                    牡蛎（熬）等分           
        '''
        quantity = ''
        medical = ''
        unit = ''
        comments = ''
        
        print 'get_component ' +  self._source_text
        
        items = re.split(ur"\uff08(\W+)\uff09", self._source_text.strip())       
        items = [item.strip() for item in items if len(item.strip()) > 0]
        
        if (len(items) == 1): #蜀椒
            medical = items[0]
        if (len(items) == 2): #蜀椒三分（去汗） or 蜀椒（去汗）
            item = items[0]
            medical = item
            matches = re.findall(ur"[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u96f6\u5341\u534a]{1,3}", item) #one to ten
            if len(matches) > 0: #format: 蜀椒三分
                quantity = matches[0]
                medical = item[0:item.rindex(quantity)]
                unit = item[item.rindex(quantity) + len(quantity):]
            comments = items[1]
        if (len(items) == 3): #蜀椒（去汗）三分
            medical = items[0]
            comments = items[1]
            item = items[2]
            matches = re.findall(ur"[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u96f6\u5341\u534a]{1,3}", item) #one to ten
            if (len(matches) > 0): #牡蛎（熬）等分
                quantity = matches[0]
                unit = item[item.rindex(quantity) + len(quantity):]
        
        print ' medical ' + medical + '\n quantity ' + quantity + '\n unit ' + unit + '\n comments ' + comments + '\n'
        return {'quantity': quantity, 'medical': medical, 'unit': unit, 'comments': comments}
      
class PrescriptionParser:
    def __init__(self, text, data_source):
        self._data_source = data_source
        self._source_text = text        
        
    def __parse_name__(self, tiaowen_item):
        '''
        Line ends with 方 (\u65b9)
        '''
        name = None
        # For SHL
        #matches = re.findall(ur"(\W*)\u65b9$", tiaowen_item)
        # For JKYL
        matches = re.findall(ur"(\W*)\u65b9\uff1a$", tiaowen_item)
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
            component_parser = SingleComponentParser(item)
            components.append(component_parser.get_component())

        ''' special case:
                        防风　桔梗　桂枝　人参　甘草各一两
        '''
        #TBD
    
        return components
        
    def get_prescriptions(self):
        prescriptions = []# name, detail, composition, source    
        
        '''
        Parse each clause to generate prescription
        '''
        # for SHL
        #matches = re.findall(ur"\s*\n+(\W*\u65b9\s+\W*)", self._source_text, re.M)
        # for JKYL
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
                    prescription.update(self._data_source)                  
                    prescriptions.append(prescription)
                    continue
                components = self.__parse_components__(item)
                if components and len(prescriptions) > 0:
                    prescriptions[-1]['components'] = components
                    continue
        return prescriptions
    
if __name__ == "__main__":
    texts = [ur'蜀椒三分（去汗）', ur'蜀椒（去汗）三分', ur'蜀椒', ur'蜀椒（去汗）', ur'蜀椒（去汗）等分']
    for item in texts:
        p = SingleComponentParser(item)
        p.get_component()
