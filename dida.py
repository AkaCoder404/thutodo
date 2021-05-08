<<<<<<< HEAD
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
from bs4 import BeautifulSoup as bs

pp = pprint.PrettyPrinter(indent=4, depth=3) 

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

  for task in incomplete_tasks:
    # print(task)
    # print(task['title'])
    print(task['title'], 'No Due Date' if 'dueDate' not in task else task['dueDate'].split('T')[0])

  
def login(username, password, session):
  request_url = 'https://api.dida365.com/api/v2/user/signon?wc=true&remember=true'
  # request_url_2 = 'https://ei.cnzz.com/stat.htm?id=1253390991&r=https%3A%2F%2Fwww.dida365.com%2F&lg=en-us&ntime=1620435542&cnzz_eid=2115462993-1620222200-https%3A%2F%2Fwww.bing.com%2F&showp=1600x900&p=https%3A%2F%2Fwww.dida365.com%2Fsignin&ei=signin_up%7Csignin_dida%7Cemail%7C0%7C&t=%E7%99%BB%E5%BD%95%20-%20%E6%BB%B4%E7%AD%94%E6%B8%85%E5%8D%95&umuuid=1793d0eeb3c53d-0356cc3c02cebc-d7e1739-144000-1793d0eeb3d4b9&h=1&rnd=1741872691'
  data = { 
    "password" : password,
    "username": username
  }
  page = request_page(request_url, data, session)
  successful = "username" in page

  if successful:
    print("登入Dida成功")
  else:
    print("登入Dida失败", page["errorCode"])


def main():
  '''main function'''
  username = input('请输入滴答账号: ')
  password = getpass.getpass('请输入滴答密码: ')
 

  # create session
  session = requests.Session()
  print(session)

  login(username, password, session)
  # load_tasks(session)
  

=======


def main():
  print("dida")
>>>>>>> 73ccedfb4ad58abf0c03bf8486ea5dcb52cad661

if __name__ == '__main__':
  main()
