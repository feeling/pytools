links_dir = '.'
links_filename = '*'
download_dir = 'down'

import ConfigParser   
cf = ConfigParser.ConfigParser()
try: 
    cf.read('config-resget.ini')
    if cf.has_option('input', 'links_dir'):
        links_dir = cf.get('input','links_dir') 
    if cf.has_option('input', 'links_filename'):
        links_filename = cf.get('input','links_filename')    
        
    if cf.has_option('output', 'download_dir'):
        download_dir = cf.get('output','download_dir') 
except Exception, e:
    print e
