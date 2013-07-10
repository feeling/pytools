#!/usr/bin/python
# -*- coding: utf-8 -*- 

'''
Created on 2012-12-19

@author: hill
'''
from lib.ordereddict import OrderedDict

def convertClassName(name):
    items = name.split('_')
    class_name = ''
    for item in items:
        class_name += item.capitalize()
    return class_name

def convertFieldName(name):
    items = name.split('_')
    class_name = ''
    for index, item in enumerate(items):
        if index:
            class_name += item.capitalize()
        else:
            class_name +=item
    return class_name

class Protocol():
    def __init__(self):
        self.request = None
        self.response = None
        
    
class ProtocolRequest():
    def __init__(self):
        self.type = None
        self.description = None
        self.data_list = []
        
    def generate_head_package(self):
        head = 'Request('
        for item in self.data_list:
            if isinstance(item, ProtocolDataItemSingelField):
                head += '(\'%s\', \'%s\'), '%(item.name, item.type)
            elif isinstance(item, ProtocolDataNull):
                head += '  '
            else:
                head += '%s, '%(convertClassName(item.name))
        head = head[0:len(head)-2] + ')'
        return head
    
    
class ProtocolResponse():
    def __init__(self):
        self.type = None
        self.direction = None
        self.description = None
        self.result = None
        self.data_list = []
    
    def generate_head_package(self):
        head = 'Response(Result, '
        for item in self.data_list:
            if isinstance(item, ProtocolDataItemSingelField):
                head += '\'%s\', '%(item.type)
            elif isinstance(item, ProtocolDataNull):
                continue
            else:
                head += '%s, '%(convertClassName(item.name))
        head = head[0:len(head)-2] + ')'
        return head
    
    
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
        self.class_name = None
        self.item_list = []

    def get_class_name(self):
        if self.class_name:
            return self.class_name
        else :
            return self.name
        
class ProtocolDataItemList():
    def __init__(self):
        self.name = None
        self.description = None
        self.class_name = None
        self.item_list = []

    def get_class_name(self):
        if self.class_name:
            return self.class_name
        else :
            return self.name
        
class ProtocolDataItemSingelField():
    def __init__(self):
        self.name = None
        self.type = None
        self.description = None

class ProtocolDataItemComplexField():
    def __init__(self):
        self.name = None
        self.description = None
        self.class_name = None
        self.field_dict = OrderedDict({})
        
    def get_class_name(self):
        if self.class_name:
            return self.class_name
        else :
            return self.name
            
        