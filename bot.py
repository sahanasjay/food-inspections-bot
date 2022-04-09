import os
import json
import requests
from sqlite_utils import Database
from slack import WebClient
from slack.errors import SlackApiError
from pprint import pprint

db = Database("food_inspections.db")

# function to get a;; ids that currently exist in db
def get_ids_in_db():
    uid_list = []
    for id in db.query("""select uid from inspections"""):
        uid_list.append(id.values())
    return print(uid_list)

get_ids_in_db()

# function to get inspections and then add them to db and query the ones we want
def get_inspections(uid_list):
    response = requests.get('https://data.princegeorgescountymd.gov/resource/umjn-t2iz.json').json()
#print(response)
#print(type(response))
    db_list = []
    temp_list = []

    uid_list = get_ids_in_db()

    for item in response:
        if 'COLLEGE PARK' in item['city']:
            if 'geocoded_column_1' in item:
                item['coordinates'] = item['geocoded_column_1']['coordinates']
                del item['geocoded_column_1']
                del item[':@computed_region_87xh_ddyp']
                item['uid'] = item['establishment_id']+item['inspection_date']
                temp_list.append(item)
            else:
                item['coordinates'] = []
                item['uid'] = item['establishment_id']+item['inspection_date']
                temp_list.append(item)

    for item in temp_list:
        if item['uid'] in uid_list:
            pass
        else:
            db_list.append(item)
        # There are no dubplicates. Deduplication code tk
    db["inspections"].insert_all(db_list, ignore = True)

    main_list = []

    for row in db.query("select * from inspections where inspection_type='Food Complaint'"):
        main_list.append(row)
        values = ['Critical Violations observed','Non-Compliant - Violations Observed']
        lst = [item for item in main_list if item['inspection_results'] in values]
    return lst

# function to send a slack message
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

#send_slack_msg()
