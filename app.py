import os
import re
import json
import requests
from sqlite_utils import Database
from slack import WebClient
from bs4 import BeautifulSoup
from slack.errors import SlackApiError
from pprint import pprint


db = Database("food_inspections.db")
link = 'https://data.princegeorgescountymd.gov/api/views/umjn-t2iz/rows.rss?'

def get_max_row_id():
    for item in db.query("""select max(rowid) as row_id from inspections"""):
        max_id = int(re.sub("]", "", re.sub("\[", "", str(list(item.values())))))
    return max_id

max_id = get_max_row_id()


def get_ids_in_db():
    uid_list = []
    for id in db.query("""select uid from inspections"""):
        tmp_lst = list(id.values())
        uid_list.extend(tmp_lst)

    return uid_list

def get_feed(link):
    items_list =[]
    times = ["5:00pm-6:00pm", "6:00pm-7:00pm", "7:00pm-8:00pm", "8:00pm-9:00pm"]
    ids = get_ids_from_items()
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'lxml-xml')

    shows_collect = soup.findAll('item')
    for show in shows_collect:
        title = show.find('title').text
