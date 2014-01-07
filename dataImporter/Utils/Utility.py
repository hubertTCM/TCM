
class Utility(object):
    def update_dict(dest, source):
        if (source is None or dest is None):
            return 
        dest.update(source)
    update_dict = staticmethod(update_dict)
    
    def runActionWhenKeyExists(key, dictionary, action):
        if (key in dictionary):
            action(dictionary[key])
    runActionWhenKeyExists = staticmethod(runActionWhenKeyExists)
            
    
