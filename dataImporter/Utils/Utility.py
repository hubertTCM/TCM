
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
    
    def add_value_if_not_none(key, value, dictionary):
        if (value is not None):
            dictionary[key] = value
            return True
        return False
    add_value_if_not_none = staticmethod(add_value_if_not_none)
    
    def append_if_not_none(value, list):
        if (value is not None):
            list.append(value)
            return True
        return False
    append_if_not_none = staticmethod(append_if_not_none)
    
    def remove_none_from(list):
        if (list is None):
            return None
        return [item for item in list if item is not None]
    remove_none_from = staticmethod(remove_none_from)
    
