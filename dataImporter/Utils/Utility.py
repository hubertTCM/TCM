# -*- coding: utf-8 -*-
import re
class Utility(object):  
    def print_dict(dictionary):
        for key, value in dictionary.items():
            print str(key) + ":" +str(value)
        print ""
    print_dict = staticmethod(print_dict)  
      
    def convert_number(chinese_number):
        if chinese_number == "半":
            return 0.5
        
        # If TEN('\u5341') is the first element, replace it with ONE
        # Remove it otherwise
        if chinese_number.find(u'\u5341') > -1:
            if chinese_number.index(u'\u5341') == 0:
                chinese_number = chinese_number.replace(u'\u5341', u'\u4e00')
            else:
                chinese_number = chinese_number.replace(u'\u5341', '')
    
        mapper = {}
        mapper[u'\u4e00'] = '1'
        mapper[u'\u4e8c'] = '2'
        mapper[u'\u4e09'] = '3'
        mapper[u'\u56db'] = '4'
        mapper[u'\u4e94'] = '5'
        mapper[u'\u516d'] = '6'
        mapper[u'\u4e03'] = '7'
        mapper[u'\u516b'] = '8'
        mapper[u'\u4e5d'] = '9'
        mapper[u'\u96f6'] = '0'
        numbers = chinese_number[:]
        return float(''.join([mapper[item] for item in numbers]) )
    convert_number = staticmethod(convert_number)  
    
    def get_value(key, dictionary, default_value = None):
        if (dictionary is None):
            return default_value
              
        if (key in dictionary):
            return dictionary[key]
        return default_value
    
    get_value = staticmethod(get_value)  
    
    def get_bool_value(key, dictionary):
        value = Utility.get_value(key, dictionary, 'False')
        return str(value) == 'True'
    
    get_bool_value = staticmethod(get_bool_value)

    def update_dict(dest, source):
        if (source is None or dest is None):
            return 
        dest.update(source)
        
    update_dict = staticmethod(update_dict)
    
    def update_dictionary_if_not_none(key, value, dictionary):
        if (value is not None):
            dictionary[key] = value
            return True
        return False
    
    update_dictionary_if_not_none = staticmethod(update_dictionary_if_not_none)
    
    def append_if_not_none(value, target_list):
        if (value is not None):
            target_list.append(value)
            return True
        return False
    
    append_if_not_none = staticmethod(append_if_not_none)
    
    def remove_none_from(source_list):
        if (list is None):
            return None
        return [item for item in source_list if item is not None]
    
    remove_none_from = staticmethod(remove_none_from)
    
    def run_action_when_key_exists(key, dictionary, action):
        if (key in dictionary):
            return action(dictionary[key])
        return None
    
    run_action_when_key_exists = staticmethod(run_action_when_key_exists)
    
    def apply_default_if_not_exist(dest, default):
        for key, value in default.items():
            if (not key in dest):
                dest[key] = value
                
    apply_default_if_not_exist = staticmethod(apply_default_if_not_exist)
      
    def remove_redundant_space(source):
        content = source.replace('&nbsp', u' ')
        content = re.sub(' +', ' ', content)
        content = re.sub('\n +', '\n', content)
        content = re.sub(u'\n+', u'\n', content)
        return content
    
    remove_redundant_space = staticmethod(remove_redundant_space)

    def escape(content):
        blank_items = [u'\xa0', '&nbsp;', '&nbsp']
        for blank_item in blank_items:
            content = content.replace(blank_item, u' ')
        return Utility.remove_redundant_space(content)
    
    escape = staticmethod(escape)
            
    
