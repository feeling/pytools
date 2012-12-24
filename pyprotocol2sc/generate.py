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
    ProtocolDataItemComplexField, convertClassName, convertFieldName
    
    
as_read_dict = {'i':'    %s//%s\n    %svar %s:int = bytes.readInt();\n',
            'I':'    %s//%s\n    %svar %s:uint = bytes.readUnsignedInt();\n',
            'h':'    %s//%s\n    %svar %s:int = bytes.readShort();\n',
            'H':'    %s//%s\n    %svar %s:uint = bytes.readUnsignedShort();\n',
            'b':'    %s//%s\n    %svar %s:int = bytes.readByte();\n',
            'B':'    %s//%s\n    %svar %s:uint = bytes.readUnsignedByte();\n',
            'string':'    %s//%s\n    %svar %sLength:uint=bytes.readUnsignedShort(); \n    %sif(%sLength) {\n        %svar %s:String = bytes.readMultiByte(%sLength,CharCode.UTF8);\n    %s}\n',
            '32s':'    %s//%s\n    %svar %s:String = bytes.readMultiByte(32,CharCode.UTF8);\n',
            '64s':'    %s//%s\n    %svar %s:String = bytes.readMultiByte(64,CharCode.UTF8);\n',
            }

as_write_dict = {'i':'    %s//%s\n    %smsgBody.writeInt(%s);\n',
            'I':'    %s//%s\n    %smsgBody.writeInt(%s);\n',
            'h':'    %s//%s\n    %smsgBody.writeShort(%s);\n',
            'H':'    %s//%s\n    %smsgBody.writeShort(%s);\n',
            'b':'    %s//%s\n    %smsgBody.writeByte(%s);\n',
            'B':'    %s//%s\n    %smsgBody.writeByte(%s);\n',
            'string':'    %s//%s\n    %smsgBody.writeMultiByte(%s, CharCode.UTF8);\n',
            '32s':'    %s//%s\n    %smsgBody.writeBytes(autoCompleByte(%s,32));\n',
            '64s':'    %s//%s\n    %smsgBody.writeBytes(autoCompleByte(%s,64));\n',
            }
python_file_code = '#!/usr/bin/python\n\
# -*- coding: utf-8 -*- \n\n'

python_client_file_header = 'from lib.packet_ids import *\n\
from lib.package import Request, Result, Response\n\
from GateWay.handler.client import append_char_id\n\
from GateWay.message import *\n\
from GateWay.protocol.client import REQUEST_HANDLERS_DICT, REQUEST_PACKAGES_DICT,RESPONSE_PACKAGES_DICT\n\
from lib import log\n\n'
python_client_file_footer = 'repeat_handler_keys = set(REQUEST_HANDLERS_DICT.keys()) & set(REQUEST_HANDLERS.keys())\n\
repeat_request_keys = set(REQUEST_PACKAGES_DICT.keys()) & set(REQUEST_PACKAGES.keys())\n\
repeat_response_keys = set(RESPONSE_PACKAGES_DICT.keys()) & set(RESPONSE_PACKAGES.keys())\n\
if repeat_handler_keys or repeat_request_keys or repeat_response_keys:\n\
    log.err(\'[ERROR] repeat key: REQUEST_HANDLERS-%s, REQUEST_PACKAGES-%s, RESPONSE_PACKAGES-%s\'%(repeat_handler_keys, repeat_request_keys, repeat_response_keys))\n\
REQUEST_HANDLERS_DICT.update(REQUEST_HANDLERS)\n\
REQUEST_PACKAGES_DICT.update(REQUEST_PACKAGES)\n\
RESPONSE_PACKAGES_DICT.update(RESPONSE_PACKAGES)'

python_game_file_header = 'from lib.packet_ids import *\n\
from GateWay.handler.game import pop_char_id\n\
from GateWay.protocol.game import REQUEST_HANDLERS_DICT\n\
from lib import log\n\n'
python_game_file_footer = 'repeat_handler_keys = set(REQUEST_HANDLERS_DICT.keys()) & set(REQUEST_HANDLERS.keys())\n\
if repeat_handler_keys:\n\
    log.err(\'[ERROR] repeat key: REQUEST_HANDLERS-%s\'%(repeat_handler_keys))\n\
REQUEST_HANDLERS_DICT.update(REQUEST_HANDLERS)'

python_gateway_file_header = 'from lib.packet_ids import *\n\
from GameServer.protocol.gateway import REQUEST_HANDLERS_DICT\n\
from lib import log\n\
from GameServer.handler.%s_handler import * \n\n'
python_gateway_file_footer = 'repeat_handler_keys = set(REQUEST_HANDLERS_DICT.keys()) & set(REQUEST_HANDLERS.keys())\n\
if repeat_handler_keys:\n\
    log.err(\'[ERROR] repeat key: REQUEST_HANDLERS-%s\'%(repeat_handler_keys))\n\
REQUEST_HANDLERS_DICT.update(REQUEST_HANDLERS)'

message_class_dict = {}

def generateCode(protocols, filename):
        generateAs(protocols, filename)
        generatePythonPacketId(protocols, filename) 
        generatePythonMessage(protocols, filename)
        generatePythonProtocol(protocols, filename)
        
        
def generateAs(protocols, filename):
    read_str = ''
    write_str = ''
    for p in protocols:
        if p.request and p.request.data_list:
            write_str += '\n//%s\npublic function write%s():void{\n'%(p.description, convertClassName(p.name))
            write_str += '    var msgBody:ByteArray = new ByteArray();\n    msgBody.endian = Endian.LITTLE_ENDIAN;\n'
            write_str +=  __generate_as_write_data_list(p.request.data_list, 0)
            write_str +='    super.send(msgBody);\n}\n'
        if p.response and p.response.data_list:
            read_str += '\n//%s\n//read%s\noverride protected function parseBodyHandle(msgHeadVo:MsgHeadVo,g2cProtocol:int,bytes:ByteArray):void{\n    var code:int = msgHeadVo.code;\n    var reason:int = msgHeadVo.reason;\n    \n    if(code == 1){\n'%(p.description, convertClassName(p.name))
            read_str +=  __generate_as_read_data_list(p.response.data_list, 1)
            read_str +='    }\n}\n'

    f = open(data_as_dir + '/as/'+filename+'.as', 'w')
    f.write(read_str)
    f.write('\n\n')
    f.write(write_str)
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

    f = open(data_python_dir + '/GateWay/'+filename+'_message.py', 'w')
    f.write(stream.getvalue())
    f.close()

def generatePythonProtocol(protocols, filename):
    request_packages_client= 'REQUEST_PACKAGES = {\n'
    request_handlers_client= 'REQUEST_HANDLERS = {\n'
    response_packages_client= 'RESPONSE_PACKAGES = {\n'
    request_handlers_gateway= 'REQUEST_HANDLERS = {\n'
    request_handlers_game= 'REQUEST_HANDLERS = {\n'
    request_handlers_define = ''
    for p in protocols:
        upper_name = p.name.upper()
        if p.request:
            request_packages_client += '    %s_REQ_%s : %s,\n'%( p.request.type, upper_name, p.request.generate_head_package())
            request_handlers_client += '    %s_REQ_%s : append_char_id,\n'%( p.request.type, upper_name)
            request_handlers_gateway += '    %s_REQ_%s : %s_handler,\n'%( p.request.type, upper_name, p.name)
            request_handlers_game += '    %s_%s_%s : pop_char_id,\n'%( p.response.type, p.response.direction, upper_name)
            request_handlers_define +='def %s_handler(p, msgid, data):\n    \n    \'\'\' %s \'\'\'\n    pass\n\n'%(p.name, p.description)
        if p.response:
            response_packages_client +='    %s_%s_%s : %s,\n'%(p.response.type,p.response.direction, upper_name, p.response.generate_head_package())
    request_packages_client += '}\n\n'
    request_handlers_client += '}\n\n'
    response_packages_client += '}\n\n'
    request_handlers_gateway +=  '}\n\n'
    request_handlers_game +=  '}\n\n'
    f = open(data_python_dir + '/GateWay/protocol/clients/'+filename+'_clients_protocol.py', 'w')
    f.write(python_file_code)
    f.write(python_client_file_header)
    f.write(request_packages_client)
    f.write(request_handlers_client)
    f.write(response_packages_client)
    f.write(python_client_file_footer)
    f.close()
    
    f = open(data_python_dir + '/GateWay/protocol/games/'+filename+'_games_protocol.py', 'w')
    f.write(python_file_code)
    f.write(python_game_file_header)
    f.write(request_handlers_game)
    f.write(python_game_file_footer)
    f.close()
    
    f = open(data_python_dir + '/GameServer/protocol/gateways/'+filename+'_gateways_protocol.py', 'w')
    f.write(python_file_code)
    f.write(python_gateway_file_header%filename)
    f.write(request_handlers_gateway)
    f.write(python_gateway_file_footer)
    f.close()

    f = open(data_python_dir + '/GameServer/handler/'+filename+'_handler.py', 'w')
    f.write(python_file_code)
    f.write(request_handlers_define)
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
    class_name  = convertClassName(item_array.get_class_name())
    if class_name not in message_class_dict:
        message = 'class %s (Array):\n    #%s\n    field=\'%s\', \'%s\'\n\n'%(class_name, field.description, field.name, field.type)
        stream.write(message)
        message_class_dict[class_name] = 1
    
def __generate_message_data_item_list(item_list, stream):
    field = item_list.item_list[0]
    __generate_message_data_item_complex_field(field,stream)
    class_name  = convertClassName(item_list.get_class_name())
    if class_name not in message_class_dict:
        message = 'class %s (List):\n    #%s\n    Field=%s\n\n'%(class_name, field.description, convertClassName(field.name))
        stream.write(message)
        message_class_dict[class_name] = 1
            
def __generate_message_data_item_single_field(item_field, stream):
    message = '(\'%s\',\'%s\')#%s\n'%( item_field.name, item_field.type, item_field.description)
    stream.write(message)

def __generate_message_data_item_complex_field(item_field, stream):
    to_generate_list =[]
    message = None
    class_name  = convertClassName(item_field.get_class_name())
    if class_name not in message_class_dict:
        message = 'class %s (Field):\n    #%s\n    fields= (\n'%(class_name, item_field.description)
        for k, v in item_field.field_dict.iteritems():
            if isinstance(v, ProtocolDataItemArray) or isinstance(v, ProtocolDataItemList) or isinstance(v, ProtocolDataItemComplexField) :
                to_generate_list.append(v)
                message += '        (\'%s\', %s),\n'%(k, convertClassName(v.get_class_name()))
            else:
                message += '        (\'%s\', \'%s\'),\n'%(k, v.type)
                
        message += '    )\n\n'
        message_class_dict[class_name] = 1
        
    for data in to_generate_list:
        if isinstance(data, ProtocolDataItemArray):
            __generate_message_data_item_array(data,stream)
        elif isinstance(data, ProtocolDataItemList):
            __generate_message_data_item_list(data,stream)
        elif isinstance(data, ProtocolDataItemSingelField):
            __generate_message_data_item_single_field(data,stream)
        elif isinstance(data, ProtocolDataItemComplexField):
            __generate_message_data_item_complex_field(data,stream)
    if message:
        stream.write(message)
    
    
    
def __generate_as_read_data_list(data_list, tabs_num=0):
    rev = ''
    for data in data_list:
        if isinstance(data, ProtocolDataItemArray):
            rev +=__generate_as_read_data_item_array(data, '', tabs_num)
        elif isinstance(data, ProtocolDataItemList):
            rev +=__generate_as_read_data_item_list(data, '', tabs_num)
        elif isinstance(data, ProtocolDataItemSingelField):
            rev +=__generate_as_read_data_item_single_field(data, '', tabs_num)
        elif isinstance(data, ProtocolDataItemComplexField):
            rev +=__generate_as_read_data_item_complex_field(data, '', tabs_num)
    return rev
            
def __generate_as_read_data_item_array(item_array, name='',tabs_num=0):
    field = item_array.item_list[0]
    if not name:
        name = item_array.name
    name = convertFieldName(name)
    blank = '    '
    blank *=tabs_num
    rev = '    %s//%s\n    %svar %sLength:uint=bytes.readUnsignedShort(); \n    %sfor(var %sIndex:int=0; %sIndex < %sLength; %sIndex++) {\n'\
            %(blank, item_array.description,blank, name,blank, name, name, name, name )
    rev += __generate_as_read_data_item_single_field(field, '', tabs_num+1)
    rev += '    %s}\n'%blank
    return rev

def __generate_as_read_data_item_list(item_list, name='',tabs_num=0):
    rev = ''
    field = item_list.item_list[0]
    if not name:
        name = item_list.name
    name = convertFieldName(name)
    blank = '    '
    blank *=tabs_num
    rev = '    %s//%s\n    %svar %sLength:uint=bytes.readUnsignedShort(); \n    %sfor(var %sIndex:int=0; %sIndex < %sLength; %sIndex++) {\n'\
            %(blank, item_list.description,blank, name, blank,name, name, name, name )
    rev += __generate_as_read_data_item_complex_field(field, '', tabs_num+1)
    rev += '    %s}\n'%blank
    return rev
    
def __generate_as_read_data_item_single_field(item_field, name='',tabs_num=0):
    if not name:
        name = item_field.name
    name = convertFieldName(name)
    blank = '    '
    blank *=tabs_num
    if item_field.type == 'string':
        rev = as_read_dict.get(item_field.type)%(blank,item_field.description,blank, name,blank,  name,blank,  name, name, blank)
    else:
        rev = as_read_dict.get(item_field.type)%(blank,item_field.description,blank, name)
    return rev

def __generate_as_read_data_item_complex_field(item_field, name ='',tabs_num=0):
    rev = ''
    blank = '    '
    blank *=tabs_num
    rev += '\n    %s//TODO 读取类型为%s 对象%s,自己构造相关对象!!!\n'%(blank, convertClassName(item_field.name), convertFieldName(name))
    
    for k, v in item_field.field_dict.iteritems():
        if isinstance(v, ProtocolDataItemArray):
            rev +=__generate_as_read_data_item_array(v, k, tabs_num)
        elif isinstance(v, ProtocolDataItemList):
            rev +=__generate_as_read_data_item_list(v, k, tabs_num)
        elif isinstance(v, ProtocolDataItemSingelField):
            rev +=__generate_as_read_data_item_single_field(v, k, tabs_num)
        elif isinstance(v, ProtocolDataItemComplexField):
            rev +=__generate_as_read_data_item_complex_field(v, k, tabs_num)
    return rev

def __generate_as_write_data_list(data_list, tabs_num=0):
    rev = ''
    for data in data_list:
        if isinstance(data, ProtocolDataItemArray):
            rev +=__generate_as_write_data_item_array(data, '', tabs_num)
        elif isinstance(data, ProtocolDataItemList):
            rev +=__generate_as_write_data_item_list(data, '', tabs_num)
        elif isinstance(data, ProtocolDataItemSingelField):
            rev +=__generate_as_write_data_item_single_field(data, '', tabs_num)
        elif isinstance(data, ProtocolDataItemComplexField):
            rev +=__generate_as_write_data_item_complex_field(data, '', tabs_num)
    return rev
            
def __generate_as_write_data_item_array(item_array, name='',tabs_num=0):
    field = item_array.item_list[0]
    if not name:
        name = item_array.name
    name = convertFieldName(name)
    blank = '    '
    blank *=tabs_num
    rev = '    %s//%s\n    %sfor(var %sIndex:int=0; %sIndex < %s.length; %sIndex++) {\n%s'\
            %(blank, item_array.description,blank, name, name, name, name, blank )
    rev += __generate_as_write_data_item_single_field(field, '', tabs_num+1)
    rev += '    %s}\n'%blank
    return rev

def __generate_as_write_data_item_list(item_list, name='',tabs_num=0):
    rev = ''
    field = item_list.item_list[0]
    if not name:
        name = item_list.name
    name = convertFieldName(name)
    blank = '    '
    blank *=tabs_num
    rev = '    %s//%s\n    %sfor(var %sIndex:int=0; %sIndex < %s.length; %sIndex++) {\n%s'\
            %(blank, item_list.description,blank, name, name, name, name, blank )
    rev += __generate_as_write_data_item_complex_field(field, '', tabs_num+1)
    rev += '    %s}\n'%blank
    return rev
    
def __generate_as_write_data_item_single_field(item_field, name='',tabs_num=0):
    if not name:
        name = item_field.name
    name = convertFieldName(name)
    blank = '    '
    blank *=tabs_num
    rev = as_write_dict.get(item_field.type)%(blank,item_field.description,blank, name)
    return rev

def __generate_as_write_data_item_complex_field(item_field, name ='',tabs_num=0):
    rev = ''
    blank = '    '
    blank *=tabs_num
    rev += '\n    %s//TODO 写入类型为%s 对象%s,自己构造相关对象提供数据写入，或者替换相关变量!!!\n'%(blank, convertClassName(item_field.name), convertFieldName(name))
    
    for k, v in item_field.field_dict.iteritems():
        if isinstance(v, ProtocolDataItemArray):
            rev +=__generate_as_write_data_item_array(v, k, tabs_num)
        elif isinstance(v, ProtocolDataItemList):
            rev +=__generate_as_write_data_item_list(v, k, tabs_num)
        elif isinstance(v, ProtocolDataItemSingelField):
            rev +=__generate_as_write_data_item_single_field(v, k, tabs_num)
        elif isinstance(v, ProtocolDataItemComplexField):
            rev +=__generate_as_write_data_item_complex_field(v, k, tabs_num)
    return rev