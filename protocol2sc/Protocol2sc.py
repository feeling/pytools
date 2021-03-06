#!/usr/bin/python
# -*- coding: utf-8 -*- 

'''
Created on 2012-12-19

@author: hill
'''
import sys  
from lib.dir_utils import get_main_dir
reload(sys)  
sys.setdefaultencoding('utf-8') 

from lib.xmltool import *
from  xml.dom import  minidom
from protocol2sc.protocol import Protocol, ProtocolRequest, ProtocolResponse,\
    ProtocolDataNull, ProtocolDataItemArray, ProtocolDataItemSingelField,\
    ProtocolDataItemList, ProtocolDataItemComplexField, ProtocolDataResult, DataStruct
from protocol2sc.config import protocol_dir, protocol_filename
import os,fnmatch
from protocol2sc.generate import generateCode
from copy import deepcopy

data_struct = DataStruct()

def parseProtocol(protocol_node, protocol):
    protocol.id = protocol_node.attributes['id'].value
    protocol.name = protocol_node.attributes['name'].value
    protocol.description = protocol_node.attributes['description'].value
    request_node = get_first_node_by_name(protocol_node, 'Request')
    if request_node:
        protocol.request = ProtocolRequest()
        parseRequest(request_node, protocol.request)
    response_node = get_first_node_by_name(protocol_node, 'Response')
    if response_node:
        protocol.response = ProtocolResponse()
        parseResponse(response_node, protocol.response)
        
def parseRequest(request_node, request):
    children = request_node.childNodes
    request.type = request_node.attributes['type'].value
    request.description = get_node_attribute_value_by_name(request_node, 'request_node')
    for node in children:
        if node.nodeName == 'DataGroup':
            parseDataGroup(node, request)
        elif node.nodeName == 'Null':
            parseNull(node, request)
    

def parseResponse(response_node, response):
    children = response_node.childNodes
    response.type = response_node.attributes['type'].value
    response.direction = get_node_attribute_value_by_name(response_node, 'direction', 'ACK')
    response.description = get_node_attribute_value_by_name(response_node, 'description')
    for node in children:
        if node.nodeName == 'DataGroup':
            parseDataGroup(node, response)
        elif node.nodeName == 'Null':
            parseNull(node, response)
        elif node.nodeName == 'Result':
            parseResult(node, response)
            
def parseResult(node, response):
    result = ProtocolDataResult()
    result.code = node.attributes['code'].value
    result.reason = node.attributes['reason'].value
    result.msg = node.attributes['msg'].value
    response.result = result

def parseDataGroup(dataGroupNode, data_container):
    data_list = data_container.data_list
    children = dataGroupNode.childNodes
    for node in children:
        if node.nodeName == 'ItemArray':
            data_list.append(parseDataTtemArray(node))
        elif node.nodeName == 'ItemList':
            data_list.append(parseDataItemList(node))
        elif node.nodeName == 'ItemSingleField':
            data_list.append(parseDataItemSingleField(node))
        elif node.nodeName == 'ItemComplexField':
            data_list.append(parseDataItemComplexField(node))
        elif node.nodeName == 'ItemRef':
            ref_item = parseItemRef(node)
            if isinstance(ref_item, (ProtocolDataItemSingelField, ProtocolDataItemArray, ProtocolDataItemComplexField, ProtocolDataItemList)):
                data_list.append(ref_item)
            else:
                print "[ERROR], item_ref:%s not in [ProtocolDataItemSingelField, ProtocolDataItemArray, ProtocolDataItemComplexField, ProtocolDataItemList]!" % ref_item.name

def parseDataStruct(dataStructNode, data_container):
    data_dict = data_container.data_dict
    children = dataStructNode.childNodes
    for node in children:
        if node.nodeName == 'ItemArray':
            item_array = parseDataTtemArray(node)
            item_array.class_name = item_array.name
            data_dict[item_array.name] = item_array
        elif node.nodeName == 'ItemList':
            item_list = parseDataItemList(node)
            item_list.class_name = item_list.name
            data_dict[item_list.name] = item_list
        elif node.nodeName == 'ItemSingleField':
            item_single = parseDataItemSingleField(node)
            item_single.class_name = item_single.name
            data_dict[item_single.name] = item_single
        elif node.nodeName == 'ItemComplexField':
            item_complex = parseDataItemComplexField(node)
            item_complex.class_name = item_complex.name
            data_dict[item_complex.name] = item_complex


def parseNull(node, data_container):
    data_container.data_list.append(ProtocolDataNull())

def parseItemRef(itemRefNode):
    ref = itemRefNode.attributes['ref'].value
    name = itemRefNode.attributes['name'].value
    description = itemRefNode.attributes['description'].value
    if ref in data_struct.data_dict:
        ref_item = deepcopy(data_struct.data_dict[ref])
        ref_item.name = name
        ref_item.description = description
        return ref_item
    else:
        print "[ERROR], item_ref:%s not exist!!!!!!!!!!!!!!!!!!!!!!!!!!!!" % ref


def parseDataTtemArray(itemArrayNode):
    children = itemArrayNode.childNodes
    item_array = ProtocolDataItemArray()
    item_array.name = itemArrayNode.attributes['name'].value
    item_array.description = itemArrayNode.attributes['description'].value
    item_array.class_name = get_node_attribute_value_by_name(itemArrayNode,'class_name')
    for node in children:
        if node.nodeName == 'ItemSingleField':
            item_array.item_list.append(parseDataItemSingleField(node))
        elif node.nodeName == 'ItemRef':
            ref_item = parseItemRef(node)
            if isinstance(ref_item, ProtocolDataItemSingelField):
                item_array.item_list.append(ref_item)
            else:
                print "[ERROR], item_ref:%s not ProtocolDataItemSingelField!!!!!!!!!!!!!!!!!!!!!!!!!!!!" % ref_item.name
    return item_array

def parseDataItemSingleField(itemSingleFieldNode):
    item_single_field = ProtocolDataItemSingelField()
    item_single_field.name = itemSingleFieldNode.attributes['name'].value
    item_single_field.type = itemSingleFieldNode.attributes['type'].value
    item_single_field.description = itemSingleFieldNode.attributes['description'].value
    return item_single_field

def parseDataItemComplexField(itemComplexFieldNode):
    item_complex_field = ProtocolDataItemComplexField()
    field_dict = item_complex_field.field_dict
    children = itemComplexFieldNode.childNodes
    item_complex_field.name  = itemComplexFieldNode.attributes['name'].value
    item_complex_field.description  = itemComplexFieldNode.attributes['description'].value
    item_complex_field.class_name  = get_node_attribute_value_by_name(itemComplexFieldNode,'class_name')
    for node in children:
        if node.nodeName == 'ItemArray':
            name = node.attributes['name'].value
            field_dict[name] = parseDataTtemArray(node)
        elif node.nodeName == 'ItemList':
            name = node.attributes['name'].value
            field_dict[name] = parseDataItemList(node)
        elif node.nodeName == 'ItemSingleField':
            name = node.attributes['name'].value
            field_dict[name] = parseDataItemSingleField(node)
        elif node.nodeName == 'ItemComplexField':
            name = node.attributes['name'].value
            field_dict[name] = parseDataItemComplexField(node)
        elif node.nodeName == 'ItemRef':
            ref_item = parseItemRef(node)
            if isinstance(ref_item, (ProtocolDataItemSingelField, ProtocolDataItemArray, ProtocolDataItemComplexField, ProtocolDataItemList)):
                field_dict[ref_item.name] = ref_item
            else:
                print "[ERROR], item_ref:%s not in [ProtocolDataItemSingelField, ProtocolDataItemArray, ProtocolDataItemComplexField, ProtocolDataItemList]!" % ref_item.name
    return item_complex_field

def parseDataItemList(itemListNode):
    children = itemListNode.childNodes
    item_list = ProtocolDataItemList()
    item_list.name = itemListNode.attributes['name'].value
    item_list.description = itemListNode.attributes['description'].value
    item_list.class_name = get_node_attribute_value_by_name(itemListNode,'class_name')
    for node in children:
        if node.nodeName == 'ItemComplexField':
            item_list.item_list.append(parseDataItemComplexField(node))
        elif node.nodeName == 'ItemRef':
            ref_item = parseItemRef(node)
            if isinstance(ref_item, ProtocolDataItemComplexField):
                item_list.item_list.append(ref_item)
            else:
                print "[ERROR], item_ref:%s not ItemComplexField!!!!!!!!!!!!!!!!!!!!!!!!!!!!" % ref_item.name
    return item_list

def parse_xml(xml_file, currentdir, currentFileName):
    doc = minidom.parse(xml_file) 
    root = doc.documentElement
    protocol_nodes = get_nodes_by_name(root, 'Protocol')
    struct_nodes = get_nodes_by_name(root, 'DataStruct')
    for struct_node in struct_nodes:
        parseDataStruct(struct_node, data_struct)
    protocols = []
    for protocol_node in protocol_nodes:
        protocol = Protocol()
        protocols.append(protocol)
        parseProtocol(protocol_node, protocol)
    generateCode(protocols, currentdir, currentFileName)

def main():
    currentdir = get_main_dir() + '/'
    print 'currentdir:', currentdir
    os.chdir(currentdir)
    patterns = ['*.xml']
    if protocol_filename != '*':
        patterns = protocol_filename.split(',')
    for root, dirs, files in os.walk(protocol_dir, True):
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name,pattern):
                    currentFileName= os.path.splitext(name)[0]
                    excelFile = os.path.join(root,name)
                    print name
                    parse_xml(excelFile, currentdir, currentFileName)
                    break

        
if __name__ == '__main__':
    main()
    raw_input('...>')