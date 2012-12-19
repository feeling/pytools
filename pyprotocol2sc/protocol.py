#!/usr/bin/python
# -*- coding: utf-8 -*- 

'''
Created on 2012-12-19

@author: hill
'''
class Protocol():
    request = None
    response = None
    
class ProtocolRequest():
    type = None
    data_list = []
    
class ProtocolResponse():
    type = None
    result = None
    data_list = []
    
class ProtocolDataNull():
    pass

class ProtocolDataResult():
    code = None
    reason = None
    msg = None

class ProtocolDataItemArray():
    name = None
    description = None
    item_list = []

class ProtocolDataItemList():
    name = None
    description = None
    item_list = []

class ProtocolDataItemSingelField():
    name = None
    type = None
    description = None

class ProtocolDataItemComplexField():
    name = None
    description = None
    field_dict = {}