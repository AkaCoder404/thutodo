# -*- coding: utf-8 -*-

# imports
import getpass 
import json 
import csv
import os
import sys
import pprint
import calendar, time, datetime
import urllib.request
import requests
import http.cookiejar
import random, string
from bs4 import BeautifulSoup as bs
from tempfile import NamedTemporaryFile 
import shutil

# for debugging
pp = pprint.PrettyPrinter(indent=4, depth=4) 

# headers 
url = 'https://www.dida365.com/'
user_agent = 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'

request_headers = {  
  'content-type': 'application/json',
  'user-agent' : user_agent,
 }

def request_page_post(request_url, data={}, session=None):
  '''request page html'''
  try:
    response = session.post(url=request_url if request_url.startswith('http') else url + request_url, data=json.dumps(data), headers=request_headers)
    # pp.pprint(response.json())
    return response.json()
  except Exception as e:
    print('Error', e, request_url)
    return {"errorCode" : e}

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
  '''read unsubmmited hw csv'''

  headers = []
  entries = []

  tempfile = NamedTemporaryFile('w+t', newline='', delete=False)
  # print(tempfile.name)

  with open(file_name, 'r') as file, tempfile:
    csvreader = csv.reader(file, delimiter=',', quotechar='"')
    csvwriter = csv.writer(tempfile, delimiter=',', quotechar='"')
    headers = next(csvreader)
    
    csvwriter.writerow(headers)
    # writerow = [col for col in entry[0:5]]
    # writerow.append('1')
    # csvwriter.writerow(writerow) 

    for entry in csvreader:
      # if not already uploaded
      if(entry[5] == '0'):
        print(entry)
        entries.append(entry)
        writerow = [col for col in entry[0:5]]
        writerow.append('1')
        csvwriter.writerow(writerow) 
      else:
        csvwriter.writerow(entry)
  
  shutil.move(tempfile.name, file_name)

  # pp.pprint(entries)
  return entries

def load_tasks(session):
  '''load upcoming tasks from dida'''
  print('下载任务信息')
  request_url = 'https://api.dida365.com/api/v2/batch/check/0'
  data = {}
  page = request_page_get(request_url, data, session)
  # pp.pprint(page)
  
  # 清单
  groups = page['projectProfiles']
  groups_id = [entry['id'] for entry in groups]
  groups_name = [entry['name'] for entry in groups]
 
 
  # tags = page['tags']
  # tags_id = [entry['etag'] for entry in tags]
  # tags_name = [entry['name'] for entry in tags]

  # 7天之内
  incomplete_tasks = page['syncTaskBean']['update']
  incomplete_hw = [task for task in incomplete_tasks if task['projectId'] == groups_id[groups_name.index("Homework")]]

  # for task in incomplete_tasks:
  #   # print(task)
  #   # print(task['title'])
  #   print(task['title'], 'No Due Date' if 'dueDate' not in task else task['dueDate'].split('T')[0])
  return groups, incomplete_hw

def upload_tasks(groups, uploaded_tasks, tasks, session):
  '''upload tasks from csv to dida'''
  print("上转作业")
  request_url = 'https://api.dida365.com/api/v2/batch/task'

  # Homework 清单 id
  group_id = ""
  for group in groups:
    if group['name'] == "Homework":
      group_id = group['id']
  
  current_time = str(datetime.datetime.now()).split(' ')
  current_time = current_time[0] + 'T' + current_time[1].split(":")[0] + ":" + current_time[1].split(":")[1] + ".000+0000"

  for task in tasks:
    # no repeat hws
    if task[0] + " " + task[1] in [uploaded_task['title'] for uploaded_task in uploaded_tasks]:
      continue
    # pp.pprint(task)
    print(task[1], "has been added")
    task_due_date = task[4].split("-")
    task_due_date = datetime.datetime(year=int(task_due_date[0]), month=int(task_due_date[1]), day=int(task_due_date[2].split(' ')[0]))
    task_due_date = task_due_date -  datetime.timedelta(hours=24)
    task_due_date = str(task_due_date).split(" ")[0] + "T16:00:00.000+0000"
    # print(task_due_date)
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
        # "sortOrder": -73117523247104,
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
    request_page_post(request_url, data, session)

def login(username, password, session):
  '''login to Dida'''
  request_url = 'https://api.dida365.com/api/v2/user/signon?wc=true&remember=true'
  data = {  "password" : password, "username": username }
  page = request_page_post(request_url, data, session)
  # print(page)
  successful = "username" in page

  if successful:
    print("登入Dida成功")
  else:
    print("登入Dida失败", page["errorCode"])

  return successful

def main():
  '''main function'''
  if len(sys.argv) > 1:
    username = sys.argv[1]
    password = sys.argv[2]
  else:
    username = input('请输入滴答账号: ')
    password = getpass.getpass('请输入滴答密码: ')

  # create session
  session = requests.Session()
  # 登入
  is_login_successful = login(username, password, session)
  
  if is_login_successful:
    # load essential information from dida
    groups, incomplete_hw_already_uploaded = load_tasks(session)
    # hw extracted by learn.py and added to csv
    learn_tasks = load_csv('csv/unsubmitted.csv')
    
    if learn_tasks: 
      # upload tasks if haven't already uploaded
      upload_tasks(groups, incomplete_hw_already_uploaded, learn_tasks, session)
    else:
      print("没有新的作业可以加到dida")

  print("dida.py完成")

if __name__ == '__main__':
  main()
