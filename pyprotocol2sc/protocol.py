#!/usr/bin/python
# -*- coding: utf-8 -*- 

'''
Created on 2012-12-19

@author: hill
'''
from lib.ordereddict import OrderedDict
class Protocol():
    def __init__(self):
        self.request = None
        self.response = None
        
    
class ProtocolRequest():
    def __init__(self):
        self.type = None
        self.data_list = []
    
    
class ProtocolResponse():
    def __init__(self):
        self.type = None
        self.result = None
        self.data_list = []
    
class ProtocolDataNull():
    pass

class ProtocolDataResult():
    def __init__(self):
        self.code = None
        self.reason = None
        self.msg = None
        

class ProtocolDataItemArray():
    def __init__(self):
        self.name = None
        self.description = None
        self.item_list = []

class ProtocolDataItemList():
    def __init__(self):
        self.name = None
        self.description = None
        self.item_list = []

class ProtocolDataItemSingelField():
    def __init__(self):
        self.name = None
        self.type = None
        self.description = None

class ProtocolDataItemComplexField():
    def __init__(self):
        self.name = None
        self.description = None
        self.field_dict = OrderedDict({})