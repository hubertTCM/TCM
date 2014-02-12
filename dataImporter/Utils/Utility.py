import re
class Utility(object):
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
            
    
