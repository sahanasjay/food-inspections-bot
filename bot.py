import os
import re
import json
import requests
from sqlite_utils import Database
from slack import WebClient
from slack.errors import SlackApiError
from pprint import pprint

db = Database("food_inspections.db")

def get_max_row_id():
    max_id = db.query("""select max(rowid) as row_id from inspections"""):
    #max_id = int(re.sub("]", "", re.sub("\[", "", str(list(item.values())))))
    return max_id

max_id = get_max_row_id()
#print(max_id)

# function to get a;; ids that currently exist in db
def get_ids_in_db():
    uid_list = []
    for id in db.query("""select uid from inspections"""):
        tmp_lst = list(id.values())
        uid_list.extend(tmp_lst)

    return uid_list

#pprint(get_ids_in_db())

# function to get inspections and then add them to db and query the ones we want
def get_inspections():
    response = requests.get('https://data.princegeorgescountymd.gov/resource/umjn-t2iz.json').json()
#print(response)
#print(type(response))
    db_list = []
    temp_list = []

    uid_list = get_ids_in_db()
    #max_id = get_max_row_id()

    for item in response:
        if 'COLLEGE PARK' in item['city']:
            if 'geocoded_column_1' in item:
                item['coordinates'] = item['geocoded_column_1']['coordinates']
                del item['geocoded_column_1']
                del item[':@computed_region_87xh_ddyp']
            else:
                item['coordinates'] = []

            item['uid'] = item['establishment_id']+item['inspection_date']

            if item['uid'] in uid_list:
                pass
            else:
                db_list.append(item)

            #db_list.append(item)

        #if item['uid'] in uid_list:
            #pass
        #else:
            #db_list.append(item)
        # There are no dubplicates. Deduplication code tk
    db["inspections"].insert_all(db_list, ignore = True)

    main_list = []

    for row in db.query("select * from inspections where inspection_type = 'Food Complaint'"):
        values = ['Critical Violations observed','Non-Compliant - Violations Observed']
        if row["inspection_results"] in values:
            main_list.append(row)
        else:
            pass
    return main_list

#pprint(get_inspections())
#new_max = get_max_row_id()
#print(new_max)

# function to send a slack message. Pulls in the previous functions.
def send_slack_msg():
    client = WebClient()
    slack_token = os.environ["SLACK_API_TOKEN"]
    client = WebClient(token=slack_token)
    for_message = get_inspections()
    pprint(for_message)
    for item in for_message:
        try:
            response = client.chat_postMessage(
            channel="slack-bots",
            text=f"🚨 Food inspection alert 🚨 A {item['inspection_type']} inspection took place at {item['name']} on {item['inspection_date']}, and the result was {item['inspection_results']}."
            )
        except SlackApiError as e:
    #You will get a SlackApiError if "ok" is False
            assert e.response["error"]

send_slack_msg()
