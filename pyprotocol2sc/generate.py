#!/usr/bin/python
# -*- coding: utf-8 -*- 

'''
Created on 2012-12-19

@author: hill
'''
from pyprotocol2sc.config import data_as_dir, data_python_dir
from cStringIO import StringIO
from pyprotocol2sc.protocol import ProtocolDataItemArray,\
    ProtocolDataItemList, ProtocolDataItemSingelField,\
    ProtocolDataItemComplexField, convertClassName
    
    
as_read_dict = {'i':'    //%s\n    var %s:int = bytes.readInt();\n',
            'I':'    //%s\n    var %s:uint = bytes.readUnsignedInt();\n',
            'h':'    //%s\n    var %s:int = bytes.readShort();\n',
            'H':'    //%s\n    var %s:uint = bytes.readUnsignedShort();\n',
            'b':'    //%s\n    var %s:int = bytes.readByte();\n',
            'B':'    //%s\n    var %s:uint = bytes.readUnsignedByte();\n',
            'string':'    //%s\n    var %s_length:uint=bytes.readUnsignedShort(); \n    if(%s_length) {\n        var %s:String = bytes.readMultiByte(%s_length,CharCode.UTF8);\n    }\n',
            '32s':'    //%s\n    var %s:String = bytes.readMultiByte(32,CharCode.UTF8);\n',
            '64s':'    //%s\n    var %s:String = bytes.readMultiByte(64,CharCode.UTF8);\n',
            }

def generateCode(protocols, filename):
        generateAs(protocols, filename)
        generatePythonPacketId(protocols, filename)
        generatePythonMessage(protocols, filename)
        generatePythonProtocol(protocols, filename)
        
        
def generateAs(protocols, filename):
    read_str = ''
    for p in protocols:
        if p.request and p.request.data_list:
            #__generate_as_read_data_list(p.request.data_list, write_stream)
            pass
        if p.response and p.response.data_list:
            read_str = 'public function read_%s(res):void{\n'
            read_str += '    var bytes:ByteArray = res.data;\n    bytes.endian=Endian.LITTLE_ENDIAN;\n    bytes.position=0;\n'
            read_str +=  __generate_as_read_data_list(p.response.data_list)
            read_str +='}'

    f = open(data_as_dir + '/'+filename+'.as', 'w')
    f.write(read_str)
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
            
    f = open(data_python_dir + '/'+filename+'_packet_id.py', 'w')
    f.write(stream.getvalue())
    f.close()

def generatePythonMessage(protocols, filename):
    stream = StringIO()
    for p in protocols:
        if p.request and p.request.data_list:
            __generate_message_data_list(p.request.data_list, stream)
        if p.response and p.response.data_list:
            __generate_message_data_list(p.response.data_list, stream)

    f = open(data_python_dir + '/'+filename+'_message.py', 'w')
    f.write(stream.getvalue())
    f.close()

def generatePythonProtocol(protocols, filename):
    request_packages= 'REQUEST_PACKAGES = {\n'
    request_handlers= 'REQUEST_HANDLERS = {\n'
    response_packages= 'RESPONSE_PACKAGES = {\n'
    for p in protocols:
        upper_name = p.name.upper()
        if p.request:
            request_packages += '    %s_REQ_%s : %s,\n'%( p.request.type, upper_name, p.request.generate_head_package())
            request_handlers += '    %s_REQ_%s : append_char_id,\n'%( p.request.type, upper_name)
        if p.response:
            response_packages +='    %s_%s_%s : %s,\n'%(p.response.type,p.response.direction, upper_name, p.response.generate_head_package())
    request_packages += '}\n\n'
    request_handlers += '}\n\n'
    response_packages += '}\n\n'
    f = open(data_python_dir + '/'+filename+'_protocol.py', 'w')
    f.write('%s%s%s'%(request_packages, request_handlers, response_packages))
    f.close()


    
def __generate_message_data_list(data_list, stream):
    for data in data_list:
        if isinstance(data, ProtocolDataItemArray):
            __generate_message_data_item_array(data,stream)
        elif isinstance(data, ProtocolDataItemList):
            __generate_message_data_item_list(data,stream)
        elif isinstance(data, ProtocolDataItemSingelField):
            __generate_message_data_item_single_field(data,stream)
        elif isinstance(data, ProtocolDataItemComplexField):
            __generate_message_data_item_complex_field(data,stream)
            
def __generate_message_data_item_array(item_array, stream):
    field = item_array.item_list[0]
    message = 'class %s (Array):\n    #%s\n    field=\'%s\', \'%s\'\n\n'%(convertClassName(item_array.name), field.description, field.name, field.type)
    stream.write(message)
    
def __generate_message_data_item_list(item_list, stream):
    field = item_list.item_list[0]
    __generate_message_data_item_complex_field(field,stream)
    message = 'class %s (List):\n    #%s\n    Field=%s\n\n'%(convertClassName(item_list.name), field.description, convertClassName(field.name))
    stream.write(message)
    
def __generate_message_data_item_single_field(item_field, stream):
    message = '(\'%s\',\'%s\')#%s\n'%( item_field.name, item_field.type, item_field.description)
    stream.write(message)

def __generate_message_data_item_complex_field(item_field, stream):
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
            __generate_message_data_item_array(data,stream)
        elif isinstance(data, ProtocolDataItemList):
            __generate_message_data_item_list(data,stream)
        elif isinstance(data, ProtocolDataItemSingelField):
            __generate_message_data_item_single_field(data,stream)
        elif isinstance(data, ProtocolDataItemComplexField):
            __generate_message_data_item_complex_field(data,stream)
    stream.write(message)
    
    
    
def __generate_as_read_data_list(data_list):
    rev = ''
    for data in data_list:
        if isinstance(data, ProtocolDataItemArray):
            rev +=__generate_as_read_data_item_array(data)
        elif isinstance(data, ProtocolDataItemList):
            rev +=__generate_as_read_data_item_list(data)
        elif isinstance(data, ProtocolDataItemSingelField):
            rev +=__generate_as_read_data_item_single_field(data)
        elif isinstance(data, ProtocolDataItemComplexField):
            rev +=__generate_as_read_data_item_complex_field(data)
    return rev
            
def __generate_as_read_data_item_array(item_array, name=''):
    field = item_array.item_list[0]
    if not name:
        name = item_array.name
    rev = '    //%s\n    var %s_length:uint=bytes.readUnsignedShort(); \n    for(var %s_index:int; %s_index < %s_length; %s_index++) {\n        '\
            %(item_array.description, name, name, name, name, name )
    rev += __generate_as_read_data_item_single_field(field)
    rev += '}'
    return rev

def __generate_as_read_data_item_list(item_list, name=''):
    rev = ''
    field = item_list.item_list[0]
    if not name:
        name = item_list.name
    rev = '    //%s\n    var %s_length:uint=bytes.readUnsignedShort(); \n    for(var %s_index:int; %s_index < %s_length; %s_index++) {\n        '\
            %(item_list.description, name, name, name, name, name )
    rev += __generate_as_read_data_item_complex_field(field)
    rev += '}'
    return rev
    
def __generate_as_read_data_item_single_field(item_field, name=''):
    if not name:
        name = item_field.name
    if item_field.type == 'string':
        rev = as_read_dict.get(item_field.type)%(item_field.description, name, name, name, name)
    else:
        rev = as_read_dict.get(item_field.type)%(item_field.description, name)
    return rev

def __generate_as_read_data_item_complex_field(item_field, name =''):
    rev = ''
    if not name:
        name = item_field.name
    rev = '// '
    for k, v in item_field.field_dict.iteritems():
        if isinstance(v, ProtocolDataItemArray):
            rev +=__generate_as_read_data_item_array(v, k)
        elif isinstance(v, ProtocolDataItemList):
            rev +=__generate_as_read_data_item_list(v, k)
        elif isinstance(v, ProtocolDataItemSingelField):
            rev +=__generate_as_read_data_item_single_field(v, k)
        elif isinstance(v, ProtocolDataItemComplexField):
            rev +=__generate_as_read_data_item_complex_field(v)
    return rev