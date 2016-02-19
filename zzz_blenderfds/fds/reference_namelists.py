"""BlenderFDS, reference to FDS namelists"""

# TODO currently not used
# TODO generalize regex

import re

DEBUG = False

def get_namelist_references(fds_file, namelist_label):
    regex = r"""
        ^&{}            # specific namelist label after newline (re.MULTILINE)
        .+?             # one or more chars of any type (not greedy) (re.DOTALL) 
        ID              # ID parameter
        \s*             # followed by zero or more spaces
        =               # an equal sign
        \s*             # followed by zero or more spaces
        ["'](.+?)["']   # ID value
    """.format(namelist_label), re.VERBOSE | re.MULTILINE | re.DOTALL
    pattern = re.compile(regex[0], regex[1])
    return pattern.findall(fds_file)
    
# Test
if __name__ == "__main__":
    # Get fds_file
    import sys
    if not sys.argv: exit()
    print("BFDS fds.add_namelist_index.add_namelist_index:", sys.argv[1])
    with open(sys.argv[1], 'r') as f:
        fds_file = f.read()
    # Add index
    print(get_namelist_references(fds_file, "MATL"))
    print(get_namelist_references(fds_file, "SURF"))
    
