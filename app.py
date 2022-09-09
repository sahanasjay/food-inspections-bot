import os
import re
import json
import datetime
import requests
from sqlite_utils import Database
from slack import WebClient
from bs4 import BeautifulSoup
from slack.errors import SlackApiError
import csv
from pprint import pprint
import dateparser


db = Database("food_inspections.db")

def get_max_date():
    for row in db.query("""select max(date) from inspections"""):
        max_date = list(row.values())
    return max_date

'''
def get_max_row_id():
    for row in db.query("""select max(rowid) from inspections"""):
        max_id = list(row.values())
    return max_id

print(get_max_row_id())

#print(get_max_row_id())
'''

def get_ids_in_db():
    uid_list = []
    for id in db.query("""select uid from inspections order by inspection_date desc"""):
        tmp_lst = list(id.values())
        uid_list.extend(tmp_lst)

    return uid_list


def get_inspections():
    infile = open("food_inspections.csv", newline='')
    reader = csv.DictReader(infile)
    uid_list = get_ids_in_db()
    db_list = []
    main_list = []
    max_date = get_max_date()
    print(max_date)
    for item in reader:
        item =  {k.lower(): v for k, v in item.items()}
        if 'COLLEGE PARK' in item['city']:
            if 'location' in item:
                item['coordinates'] = item['location']
                del item['location']
            else:
                item['coordinates'] = []


            item['uid'] = item['establishment_id']+'-'+item['inspection_date']
            item['date'] = datetime.datetime.strftime(dateparser.parse(item['inspection_date']), '%Y-%m-%d')
            #db_list.append(item)

            if item['uid'] in uid_list:
                print(f"{item['uid']} already in db")
            else:
                db_list.append(item)

    db["inspections"].insert_all(db_list, ignore = True)

    #values = ['Critical Violations observed','Non-Compliant - Violations Observed']

    for row in db.query("""select * from inspections where inspection_results in ('Critical Violations observed','Non-Compliant - Violations Observed') and date > ? order by date""", max_date):
            #row['violation']
            main_list.append(row)

    return main_list

#print(len(get_inspections()))
#nmprint(get_inspections())


def send_slack_msg():
    for_message = get_inspections()
    restaurant_names = []
    for item in for_message:
        violations = []
        for k,v in item.items():
            if v == 'Out of Compliance':
                violations.append(k)
        item['violations'] = violations
        estab_id = item['establishment_id']
        restaurant_names.append(item['name'].lower())
        query = f"select * from inspections where establishment_id={estab_id}"
        previous = [item for item in db.query(query)]
        values = ['Critical Violations observed','Non-Compliant - Violations Observed']
        prev_violations = [item for item in previous if item['inspection_results'] in values]
        number_previous_value = len(previous)
        number_prev_violations = len(prev_violations)
        item['previous_number'] = number_previous_value
        item['prev_violations'] = number_prev_violations
        print(item)
    main_msg = len(for_message)
    restaurant_names = '\n- '.join(restaurant_names)
    #print(restaurant_names)
    message = f":rotating_light: *FOOD INSPECTION SUMMARY* :rotating_light:\n\n:wave:Hello <!channel>, Bot here with your weekly summary.\n\n This week, there were *{main_msg}* inspections in College Park resulting in a violation.\n\n Affected businesses include:\n- {restaurant_names}\n\nSee my :thread: for details."
    client = WebClient()
    #<!channel>
    slack_token = os.environ["SLACK_API_TOKEN"]
    client = WebClient(token=slack_token)
    ts_id = ""
    if main_msg > 0:
        try:
            response = client.chat_postMessage(
            channel="news_desk",
            blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": message}}]
            #text=f"🚨 Food Inspection result: {item['inspection_type']} 🚨 Inspection took place at {item['name']} on {item['inspection_date']}, and the result was {item['inspection_results']}."
            )
            ts_id = ts_id+response['ts']
        except SlackApiError as e:
    #You will get a SlackApiError if "ok" is False
            assert e.response["error"]
        for item in for_message:
            violations = item['violations']
            violations = '\n- '.join(violations)
            try:
                #estab_id = item['establishment_id']
                #number_previous = [item for item in db.query("select count(*) from inspections where establishment_id=?", estab_id)]
                #number_previous = new = re.sub("]", "", re.sub("\[", "", str(number_previous)))
                #number_violation = [item for item in db.query("select count(*) from inspections where establishment_id=? and inspection_results in ('Critical Violations observed','Non-Compliant - Violations Observed')", estab_id)]
                #number_violation = re.sub("]", "", re.sub("\[", "", str(number_violation)))
                response = client.chat_postMessage(
                channel="news_desk",
                thread_ts=ts_id,
                blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": f"A {item['inspection_type']} inspection took place at {item['name']} on {item['date']}, and the result was *{item['inspection_results']}*.\n\nThe establishment didn't comply with regulations for: \n- {violations}\n\nThis establishment has been through *{item['previous_number']}* inspections, *{item['prev_violations']}* of which resulted in a violation.\n\nThe addy: {item['address_line_1']}\n\nFor more: <https://data.princegeorgescountymd.gov/Health/Food-Inspection/umjn-t2iz|Here's the link to the data>.\n\nWant to file an MPIA? <https://www.princegeorgescountymd.gov/DocumentCenter/View/4629/MPIA-Request-Form-PDF| Here's a form> for that."}}]
                #text=f"🚨 Food Inspection result: {item['inspection_type']} 🚨 Inspectiontook place at {item['name']} on {item['inspection_date']}, and the result was {item['inspection_results']}."
                )
            except SlackApiError as e:
    #You will get a SlackApiError if "ok" is False
                assert e.response["error"]
    else:
        try:
            response = client.chat_postMessage(
            channel="news_desk",
            blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": f":wave: Hello there! Bot here with your weekly summary.\n\n*Nothing to report this week*: There were *{main_msg}* inspections that resulted in a violation in College Park. Check back in next week!"}}]
            #text=f"🚨 Food Inspection result: {item['inspection_type']} 🚨 Inspectiontook place at {item['name']} on {item['inspection_date']}, and the result was {item['inspection_results']}."
            )
        except SlackApiError as e:
            assert e.response["error"]

send_slack_msg()

#def make_thread():
    #client = WebClient()
    #slack_token = os.environ["SLACK_API_TOKEN"]
    #client = WebClient(token=slack_token)
    #for_message = get_inspections()
    #ts_id = send_slack_msg()
    #for item in for_message:
        #try:
            #response = client.chat_postMessage(
            #channel="slack-bots",
            #thread_ts=ts_id,
            #blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": f"A {item['inspection_type']} inspection took place at {item['name']} on {item['inspection_date']}, and the result was {item['inspection_results']} \n For more: <https://data.princegeorgescountymd.gov/Health/Food-Inspection/umjn-t2iz|Here's the link to the data>. \n Want to file an MPIA? <https://www.princegeorgescountymd.gov/DocumentCenter/View/4629/MPIA-Request-Form-PDF| Here's a form> for that."}}]
            #text=f"🚨 Food Inspection result: {item['inspection_type']} 🚨 Inspectiontook place at {item['name']} on {item['inspection_date']}, and the result was {item['inspection_results']}."
            #)
        #except SlackApiError as e:
    #You will get a SlackApiError if "ok" is False
            #assert e.response["error"]

#make_thread()
