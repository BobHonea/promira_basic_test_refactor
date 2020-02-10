'''
Created on Feb 8, 2020

@author: Asus
'''
      
      
      
import camelot
tables = camelot.read_pdf("c:\\Users\\Asus\\SST26VF016B-pp12-13.pdf")
tables
<TableList n=1>
tables.export('foo.csv', f='csv', compress=True) # json, excel, html
tables[0]
<Table shape=(7, 7)>
tables[0].parsing_report
{
    'accuracy': 99.02,
    'whitespace': 12.24,
    'order': 1,
    'page': 1
}
tables[0].to_csv('foo.csv') # to_json, to_excel, to_html
tables[0].df # get a pandas DataFrame!      