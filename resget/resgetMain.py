#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2012-12-8

@author: Administrator
'''
import sys  
from lib.dir_utils import get_main_dir
reload(sys)  
#sys.setdefaultencoding('utf-8') 

import os,fnmatch
from resget.configs import links_dir, links_filename, download_dir
import re

pattern = re.compile(r'GET\s(http\://.*?)\sHTTP/1\.[01]')

def downFile(url):
    path = url.split('//')[1].split('?')[0]
    fileNameArray = path.rsplit('/',1)
    dirName = download_dir + fileNameArray[0]
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    cmd = 'curl -o '+download_dir + path+' '+url
    os.system(cmd)
    
def parseFile(linkFile):
    try:
        f = open(linkFile, 'r');
        line = f.readline()
        match = pattern.match(line)
        if match:
            url = match.group(1)
            if url and len(url)>10:
                downFile(url)
        
    except Exception,e:
        print e
    
if __name__ == '__main__':
    global currentdir
    global currentFileName
    try:
        currentdir = get_main_dir()+'/'
        print 'currentdir:', currentdir
        os.chdir(currentdir)
        for root, dirs, files in os.walk(links_dir, True):   
            for name in files:
                if fnmatch.fnmatch(name,links_filename):
                    linkFile = os.path.join(root,name)
                    print linkFile
                    parseFile(linkFile)
    except Exception,e:
        print e
    raw_input('input enter...>') 