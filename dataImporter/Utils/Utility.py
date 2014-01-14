
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
        return value == 'True'
    
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
            
    
