"""BlenderFDS, add an index to FDS namelists"""

# TODO currently not used
# TODO generalize regex

import re

DEBUG = True

regex = r"""
    (?P<namelist>   # namelist, group "namelist"
        ^&                              # ampersand after newline (re.MULTILINE)
        (?P<label>[A-Z0-9_]{4})         # namelist label, 4 chars, group "fds_label"
        [,\s]+                          # followed by one or more separators of any kind
        (?P<params>                     # namelist parameters, group "fds_params"
            (?: '[^']*?' | "[^"]*?" | [^'"] )*?     # namelist params; protect chars in strings, "no params" allowed by *
        )
    [,\s]*          # followed by zero or more separators of any kind
    /               # closing slash, anything outside &.../ is a comment and is ignored
    )    
""", re.VERBOSE | re.MULTILINE | re.DOTALL

def add_namelist_index(fds_file):
    start = 0
    namelist_index = dict()
    pattern = re.compile(regex[0], regex[1])
    while True:
        m = pattern.search(fds_file, start)
        if not m: break
        label = m.group("label")
        end = m.end("namelist")
        print(label,end)
        if label in namelist_index: namelist_index[label] += 1
        else: namelist_index[label] = 1
        fds_index = " [{} {}]".format(label,namelist_index[label])
        fds_file = fds_index.join((fds_file[:m.end("namelist")],fds_file[m.end("namelist"):]))
        start = m.end("namelist")
    return fds_file
    
# Test
if __name__ == "__main__":
    # Get fds_file
    import sys
    if not sys.argv: exit()
    print("BFDS fds.add_namelist_index.add_namelist_index:", sys.argv[1])
    with open(sys.argv[1], 'r') as f:
        fds_file = f.read()
    # Add index
    print(add_namelist_index(fds_file))
