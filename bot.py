import os
import json
import requests
from sqlite_utils import Database
from slack import WebClient
from slack.errors import SlackApiError



def get_inspections():
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

    main_list = []

    for row in db.query("select * from inspections where city= 'COLLEGE PARK' and inspection_type='Food Complaint'"):
        main_list.append(row)
        values = ['Critical Violations observed','Non-Compliant - Violations Observed']
        lst = [item for item in main_list if item['inspection_results'] in values]
    return lst


for_message = get_inspections()
print(for_message)

def send_slack_msg():
    client = WebClient()
    slack_token = os.environ["SLACK_API_TOKEN"]
    client = WebClient(token=slack_token)
    for item in for_message:
        try:
            response = client.chat_postMessage(
            channel="slack-bots",
            text=f"🚨 Food inspection alert 🚨 A {item['inspection_type']} inspection took place at {item['name']}, and the result was {item['inspection_results']}."
            )
        except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
            assert e.response["error"]

send_slack_msg()
