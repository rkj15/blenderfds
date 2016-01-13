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

