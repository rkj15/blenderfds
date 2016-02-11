#!/usr/bin/python3
# Color terminal output <http://blenderfds.org/>.
# Copyright (C) 2016 Emanuele Gissi
# Released under the terms of the GNU GPL version 3 or any later version.

__all__ = ["print_h1", "print_h2", "print_ok", "print_warn", "print_fail"]

def print_h1(msg): print("\033[1;34m{}\033[0m".format(msg))
def print_h2(msg): print("\033[1;35m{}\033[0m".format(msg))
def print_ok(msg): print("\033[1;32m{}\033[0m".format(msg))
def print_warn(msg): print("\033[1;33m{}\033[0m".format(msg))
def print_fail(msg): print("\033[1;31m{}\033[0m".format(msg))

def test():
    print_h1("Test h1")
    print_h2("Test h2")
    print("Normal")
    print_ok("Test ok")
    print_warn("Test warn")
    print_fail("Test fail")

def main():
    test()
    
if __name__ == "__main__":
    main()
