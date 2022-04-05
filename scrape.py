import json
import requests
from pprint import pprint
from sqlite_utils import Database

response = requests.get('https://data.princegeorgescountymd.gov/resource/umjn-t2iz.json').json()
#print(response)
#print(type(response))

db_list = []

for item in response:
    if 'geocoded_column_1' in item:
        item['coordinates'] = item['geocoded_column_1']['coordinates']
        del item['geocoded_column_1']
        del item[':@computed_region_87xh_ddyp']
    else:
        item['coordinates'] = []
    db_list.append(item)

db = Database("food_inspections.db")
inspections = db["inspections"]

db['inspections'].insert_all(db_list, ignore = True)

def func():
    main_list = []
    for row in db.query("select * from inspections where city= 'COLLEGE PARK' and inspection_type='Food Complaint'"):
        main_list.append(row)
        values = ['Critical Violations observed','Non-Compliant - Violations Observed']
        lst = [item for item in main_list if item['inspection_results'] in values]
        return lst

for_message = func()
#for row in db["inspections"].rows_where("city = ?", ['COLLEGE PARK']):
    #pprint(row)
#print(response)
    #print(item['establishment_id'])
    #print(item['coordinates'])
    #del item['geocoded_column_1']


#establishment_id = json.loads(response)
#print(type(establishment_id))
