# -*- coding: utf-8 -*-
import re
class Utility(object): 
    def get_dict_from(line): 
        return_value = {}
        items = filter(lambda(x): len(x) > 0, line.split('\t'))
        for item in items:
            key_pairs = filter(lambda(x): len(x) > 0, item.split(':', 1))
            if len(key_pairs)== 0:
                continue
            key = key_pairs[0]
            value = None
            if len(key_pairs)== 2:
                value = key_pairs[1]
            return_value[key] = value
        return return_value
    get_dict_from = staticmethod(get_dict_from)
    
    def convert_dict_to_string(dictionary):
        line = ''
        for key, value in dictionary.items():
            line += '\t' + str(key) + ":" +str(value)
        return line
    convert_dict_to_string = staticmethod(convert_dict_to_string)
      
    def convert_number(chinese_number): 
        if chinese_number == "半":
            return 0.5
        
        other_mapper = {}
        other_mapper[u'十'] = 1
        other_mapper[u'百'] = 2
        
        for key, value in other_mapper.items():
            if chinese_number.find(key) == 0:
                chinese_number = u'一' + chinese_number
            if chinese_number[-1] == key:
                chinese_number = chinese_number[:len(chinese_number)-1]
                for i in range(value):
                    chinese_number+= u'\u96f6'
                        
    
        number_mapper = {}
        number_mapper[u'\u4e00'] = '1'
        number_mapper[u'\u4e8c'] = '2'
        number_mapper[u'\u4e09'] = '3'
        number_mapper[u'\u56db'] = '4'
        number_mapper[u'\u4e94'] = '5'
        number_mapper[u'\u516d'] = '6'
        number_mapper[u'\u4e03'] = '7'
        number_mapper[u'\u516b'] = '8'
        number_mapper[u'\u4e5d'] = '9'
        number_mapper[u'\u96f6'] = '0'
        
        for key in other_mapper.keys():
            number_mapper[key] = ''
        
        numbers = chinese_number[:]
        return float(''.join([number_mapper[item] for item in numbers]) )
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
        if (source_list is None):
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
    
    def remove_blank_space(content):
        return re.sub('[ \u3000]+', '', content)
    remove_blank_space = staticmethod(remove_blank_space)
      
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
    
if __name__ == "__main__":
    print Utility.convert_number(u'四十')
    print Utility.convert_number(u'十一')
    print Utility.convert_number(u'十')
    print Utility.convert_number(u'一十')
    print Utility.convert_number(u'一十一')
            
    
