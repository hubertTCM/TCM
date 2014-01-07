
class Utility(object):
    def update_dict(dest, source):
        if (source is None or dest is None):
            return 
        dest.update(source)
    update_dict = staticmethod(update_dict)
    
    def run_action_when_key_exists(key, dictionary, action):
        if (key in dictionary):
            action(dictionary[key])
    run_action_when_key_exists = staticmethod(run_action_when_key_exists)
    
    def apply_default_if_not_exist(dest, default):
        for key, value in default.items():
            if (not key in dest):
                dest[key] = value
    apply_default_if_not_exist = staticmethod(apply_default_if_not_exist)
            
    
