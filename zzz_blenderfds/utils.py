"""BlenderFDS, other utilities"""

# Check if a quantity is an iterable type

def is_iterable(var):
    """Check if var is iterable or not
    
    >>> is_iterable("hello"), is_iterable((1,2,3)), is_iterable({1,2,3})
    (False, True, True)
    """
    # A str is iterable in Py... not what I want
    if isinstance(var, str): return False
    # Let's try and fail nicely
    try:
        for item in var: break
    except TypeError: return False
    return True

# Collection of classes

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

# Write to file
        
def is_writable(filepath):
    """Check if filepath is writable"""
    return write_to_file(filepath, "Test")

def write_to_file(filepath, text_file):
    """Write text_file to filepath"""
    if text_file is None: text_file = str()
    try:
        with open(filepath, "w") as out_file: out_file.write(text_file)
        return True
    except IOError:
        return False

