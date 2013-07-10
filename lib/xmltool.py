#!/usr/bin/python
# -*- coding: utf-8 -*- 

'''
Created on 2012-12-19

@author: hill
'''
def get_attrvalue(node, attrname):
    return node.getAttribute(attrname) if node else ''

def get_nodevalue(node, index = 0):
    return node.childNodes[index].nodeValue if node else ''

def get_nodes_by_name(node,name):
    return node.getElementsByTagName(name) if node else []

def get_first_node_by_name(node,name):
    nodes = get_nodes_by_name(node,name)
    return nodes[0] if nodes else None

def get_node_attribute_value_by_name(node,name, default_value = ''):
    if node.hasAttribute(name):
        attribute = node.attributes[name]
        return attribute.value if attribute else default_value
    else:
        return default_value