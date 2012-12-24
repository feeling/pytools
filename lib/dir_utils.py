#!/usr/bin/python
# -*- coding: utf-8 -*- 

'''
Created on 2012-12-24

@author: hill
'''
import sys
def main_is_frozen():
    """Return ``True`` if we're running from a frozen program."""
    import imp
    return (
        # new py2exe
        hasattr(sys, "frozen") or
        # tools/freeze
        imp.is_frozen("__main__"))

def get_main_dir():
    """Return the script directory - whether we're frozen or not."""
    import os
    if main_is_frozen():
        return os.path.abspath(os.path.dirname(sys.executable))
    return os.path.abspath(os.path.dirname(sys.argv[0])) 