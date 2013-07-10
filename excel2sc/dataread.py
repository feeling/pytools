#!/usr/bin/python
# -*- coding: utf-8 -*- 
'''
Created on 2012-12-13

@author: hill
'''
from struct import unpack, calcsize
f = open('out/break_through_dungeon.dat','r')
data = f.read()
print repr(data), len(data)
length = unpack('H', data[0:2])
id = unpack('I', data[2:6])
namelen = unpack('H',data[6:8])
print calcsize('I')
print namelen;