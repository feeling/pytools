#!/usr/bin/python
# -*- coding: utf-8 -*- 

'''
Created on 2012-12-19

@author: hill
'''
from pyprotocol2sc.config import data_as_dir
from cStringIO import StringIO
from pyprotocol2sc.protocol import ProtocolDataNull, ProtocolDataItemArray,\
    ProtocolDataItemList, ProtocolDataItemSingelField,\
    ProtocolDataItemComplexField

def convertClassName(name):
    items = name.split('_')
    class_name = ''
    for item in items:
        class_name += item.capitalize()
    return class_name

def generateCode(protocols, filename):
        generateAs(protocols, filename)
        generatePythonPacketId(protocols, filename)
        generatePythonMessage(protocols, filename)
        generatePythonProtocol(protocols, filename)
        
        
def generateAs(protocols, filename):
    f = open(data_as_dir + '/'+filename+'.as', 'w')
    f.write('')
    f.close()

def generatePythonPacketId(protocols, filename):
    stream = StringIO()
    for p in protocols:
        packet_id = int(p.id)
        upper_name = p.name.upper()
        if p.request:
            stream.write('\'\'\'  %s  \'\'\'\n%s_REQ_%s = %d\n'%(p.description, p.request.type, upper_name, packet_id))
            packet_id += 1
        if p.response:
            stream.write('%s_ACK_%s = %d\n\n\n'%(p.response.type, upper_name, packet_id))
            
    f = open(data_as_dir + '/'+filename+'_packet_id.py', 'w')
    f.write(stream.getvalue())
    f.close()

def generatePythonMessage(protocols, filename):
    stream = StringIO()
    for p in protocols:
        packet_id = int(p.id)
        upper_name = p.name.upper()
        if p.request and p.request.data_list:
            __generate_data_list(p.request.data_list, stream)
        if p.response and p.response.data_list:
            __generate_data_list(p.response.data_list, stream)

    f = open(data_as_dir + '/'+filename+'_message.py', 'w')
    f.write(stream.getvalue())
    f.close()

def generatePythonProtocol(protocols, filename):
    f = open(data_as_dir + '/'+filename+'_protocol.py', 'w')
    f.write('')
    f.close()


    
def __generate_data_list(data_list, stream):
    for data in data_list:
        if isinstance(data, ProtocolDataItemArray):
            __generate_data_item_array(data,stream)
        elif isinstance(data, ProtocolDataItemList):
            __generate_data_item_list(data,stream)
        elif isinstance(data, ProtocolDataItemSingelField):
            __generate_data_item_single_field(data,stream)
        elif isinstance(data, ProtocolDataItemComplexField):
            __generate_data_item_complex_field(data,stream)
            
def __generate_data_item_array(item_array, stream):
    field = item_array.item_list[0]
    message = 'class %s (Array):\n    #%s\n    field=\'%s\', \'%s\'\n\n'%(convertClassName(item_array.name), field.description, field.name, field.type)
    stream.write(message)
    
def __generate_data_item_list(item_list, stream):
    field = item_list.item_list[0]
    __generate_data_item_complex_field(field,stream)
    message = 'class %s (List):\n    #%s\n    Field=%s\n\n'%(convertClassName(item_list.name), field.description, convertClassName(field.name))
    stream.write(message)
    
def __generate_data_item_single_field(item_field, stream):
    message = '(\'%s\',\'%s\')#%s\n'%( item_field.name, item_field.type, item_field.description)
    stream.write(message)

def __generate_data_item_complex_field(item_field, stream):
    to_generate_list =[]
    message = 'class %s (Field):\n    #%s\n    fields= (\n'%(convertClassName(item_field.name), item_field.description)
    for k, v in item_field.field_dict.iteritems():
        if isinstance(v, ProtocolDataItemArray) or isinstance(v, ProtocolDataItemList) or isinstance(v, ProtocolDataItemComplexField) :
            to_generate_list.append(v)
            message += '        (\'%s\', %s),\n'%(k, convertClassName(v.name))
        else:
            message += '        (\'%s\', \'%s\'),\n'%(k, v.type)
            
    message += '    )\n\n'
    for data in to_generate_list:
        if isinstance(data, ProtocolDataItemArray):
            __generate_data_item_array(data,stream)
        elif isinstance(data, ProtocolDataItemList):
            __generate_data_item_list(data,stream)
        elif isinstance(data, ProtocolDataItemSingelField):
            __generate_data_item_single_field(data,stream)
        elif isinstance(data, ProtocolDataItemComplexField):
            __generate_data_item_complex_field(data,stream)
    stream.write(message)
    