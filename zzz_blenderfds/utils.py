"""BlenderFDS, other utilities"""

def isiterable(var):
    """Check if var is iterable or not
    
    >>> isiterable("hello"), isiterable((1,2,3)), isiterable({1,2,3})
    (False, True, True)
    """
    # A str is iterable in Py... not what I want
    if isinstance(var, str): return False
    # Let's try and fail nicely
    try:
        for item in var: break
    except TypeError: return False
    return True

class ClsList(list):
    """List of classes"""

    def __contains__(self,key):
        if isinstance(key,str):
            for value in self:
                if value.__name__ == key: return True
            else: return False
        return list.__contains__(self,key)
    
    def __getitem__(self,key):
        if isinstance(key,str):
            for value in self:
                if value.__name__ == key: return value
                raise KeyError(key)    
        return super().__getitem__(self,key)

    def get(self,key,default=None):
        for value in self:
            if value.__name__ == key: return value
        return default

    def get_by_fds_label(self,key,default=None):
        if not key: return default
        for value in self:
            if value.fds_label == key: return value
        return default
