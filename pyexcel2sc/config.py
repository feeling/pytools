excel_dir = '.'
data_sql_dir = '.'
data_as_dir = '.'
data_dat_dir = '.'
isGenerateCreateSql = 0
isGenerateAs = 0
excel_filename = '*'
xml_dir = '.'
xml_filename = '*'

import ConfigParser   
cf = ConfigParser.ConfigParser()
try: 
    cf.read('config-excel.ini')
    if cf.has_option('input', 'excel_dir'):
        excel_dir = cf.get('input','excel_dir') 
    if cf.has_option('input', 'excel_filename'):
        excel_filename = cf.get('input','excel_filename')    
        
    if cf.has_option('output', 'data_sql_dir'):
        data_sql_dir = cf.get('output','data_sql_dir') 
    if cf.has_option('output', 'data_as_dir'):
        data_as_dir = cf.get('output','data_as_dir') 
    if cf.has_option('output', 'data_dat_dir'):
        data_dat_dir = cf.get('output','data_dat_dir') 
    if cf.has_option('output', 'isGenerateCreateSql'):
        isGenerateCreateSql = cf.getint('output','isGenerateCreateSql')
    if cf.has_option('output', 'isGenerateAs'):
        isGenerateAs = cf.getint('output','isGenerateAs')
        
    if cf.has_option('input', 'xml_dir'):
        xml_dir = cf.get('input','xml_dir') 
    if cf.has_option('input', 'xml_filename'):
        xml_filename = cf.get('input','xml_filename')  
except Exception, e:
    print e
