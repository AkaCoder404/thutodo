# -*- coding: utf-8 -*-

# imports
import getpass 
import json 
import csv
import os
import pprint
import calendar, time, datetime
import urllib.request
import requests
import http.cookiejar
import random, string
from bs4 import BeautifulSoup as bs

pp = pprint.PrettyPrinter(indent=4, depth=4) 

cookie = http.cookiejar.MozillaCookieJar()
handler = urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(handler)
urllib.request.install_opener(opener)

# headers 
url = 'https://www.dida365.com/'
user_agent = 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'

request_headers = {  
  'content-type': 'application/json',
  'user-agent' : user_agent,
 }

# post
def request_page(request_url, data={}, session=None):
  '''request page html'''
  try:
    response = session.post(url=request_url if request_url.startswith('http') else url + request_url, data=json.dumps(data), headers=request_headers)
    # pp.pprint(response.json())
    return response.json()
  except Exception as e:
    print('Error', e, request_url)

# get 
def request_page_get(request_url, data={}, session=None):
  try:
    response = session.get(url=request_url if request_url.startswith('http') else url + request_url)
    # pp.pprint(response.__dict__)
    return response.json()
  except Exception as e:
    print('Error', e, request_url)

def load_json(request_url, data={}):
  '''load json data'''

def load_csv(file_name):
  '''read csv'''

  headers = []
  entries = []

  with open(file_name, 'r') as f:
    csvreader = csv.reader(f)
    # print(csvreader)
    headers = next(csvreader)
    for entry in csvreader:
      # print(entry)
      if(entry[5] == '0'):
        entries.append(entry)

  # pp.pprint(entries)
  return entries


def load_tasks(session):
  '''load_tasks'''
  print('load task')
  request_url = 'https://api.dida365.com/api/v2/batch/check/0'
  data = {}
  page = request_page_get(request_url, data, session)
  # pp.pprint(page)
  
  # 清单
  groups = page['projectProfiles']
  tags = page['tags']

  # 7天之内
  incomplete_tasks = page['syncTaskBean']['update']

  # for task in incomplete_tasks:
  #   # print(task)
  #   # print(task['title'])
  #   print(task['title'], 'No Due Date' if 'dueDate' not in task else task['dueDate'].split('T')[0])
  return groups


def upload_tasks(groups, tasks, session):
  '''upload tasks from csv to online'''
  request_url = 'https://api.dida365.com/api/v2/batch/task'

  # Homework 清单
  group_id = ""
  for group in groups:
    if group['name'] == "Homework":
      group_id = group['id']
      print(group_id)
  
  current_time = str(datetime.datetime.now()).split(' ')
  current_time = current_time[0] + 'T' + current_time[1].split(":")[0] + ":" + current_time[1].split(":")[1] + ".000+0000"

  for task in tasks:
    # pp.pprint(task)
    task_due_date = task[4].split("-")
    task_due_date = datetime.datetime(year=int(task_due_date[0]), month=int(task_due_date[1]), day=int(task_due_date[2].split(' ')[0]))
    task_due_date = task_due_date -  datetime.timedelta(hours=24)
    task_due_date = str(task_due_date).split(" ")[0] + "T16:00:00.000+0000"
    print(task_due_date)
    random_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(24))
    data = {
    "add": [
      {
          "assignee": None,
          "content": task[2],
          "createdTime": str(current_time),
          "dueDate": None,
          "exDate": [],
          "id": str(random_id),
          "isAllDay": "true",
          "isFloating": "false",
          "items": [],
          "kind": None,
          "modifiedTime": str(current_time),
          "priority": 0,
          "progress": 0,
          "projectId": group_id,
          "reminders": [],
          "repeatFlag": None,
          "sortOrder": -73117523247104,
          "startDate": task_due_date,
          "status": 0,
          "tags": [],
          "timeZone": "Asia/Shanghai",
          "title": task[0] + " " + task[1]
      }
    ],
    "delete": [],
    "update": []
    }
    request_page(request_url, data, session)

def login(username, password, session):
  '''login to Dida'''
  request_url = 'https://api.dida365.com/api/v2/user/signon?wc=true&remember=true'
  data = {  "password" : password, "username": username }
  page = request_page(request_url, data, session)
  # print(page)
  successful = "username" in page

  if successful:
    print("登入Dida成功")
  else:
    print("登入Dida失败", page["errorCode"])

  return successful

def main():
  '''main function'''
  username = input('请输入滴答账号: ')
  password = getpass.getpass('请输入滴答密码: ')

 
 
  # create session
  session = requests.Session()
  # 登入
  is_login_successful = login(username, password, session)
  groups = load_tasks(session)

  # pp.pprint(groups)

  if is_login_successful:
    # hw from learn
    learn_tasks = load_csv('csv/unsubmitted.csv')
    upload_tasks(groups, learn_tasks, session)

if __name__ == '__main__':
  main()
