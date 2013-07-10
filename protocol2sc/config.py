protocol_dir = '.'
data_python_dir = '.'
data_as_dir = '.'
protocol_filename = '*'

import ConfigParser   
cf = ConfigParser.ConfigParser()
try: 
    cf.read('config-protocol.ini')
    if cf.has_option('input', 'protocol_dir'):
        protocol_dir = cf.get('input','protocol_dir') 
    if cf.has_option('input', 'protocol_filename'):
        protocol_filename = cf.get('input','protocol_filename')    
        
    if cf.has_option('output', 'data_python_dir'):
        data_python_dir = cf.get('output','data_python_dir') 
    if cf.has_option('output', 'data_as_dir'):
        data_as_dir = cf.get('output','data_as_dir') 
except Exception, e:
    print e
