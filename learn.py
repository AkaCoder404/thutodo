# -*- coding: utf-8 -*-

# imports
import getpass # obscure text on terminal
import argparse # parser for command line options 
import json 
import sys # handle command line arguments
import csv
import os # handle directory information
import pprint # pretty printer for debugging
import calendar, time, datetime # time stamp
import urllib.request # library for opening urls
import http.cookiejar # cookie handling for HTTP client


from bs4 import BeautifulSoup as bs

# headers and handlers
url = 'https://learn.tsinghua.edu.cn'
user_agent = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"
request_headers = {
  'User-Angent' : user_agent,
  'Connection' : 'keep-alive'
}

cookie = http.cookiejar.MozillaCookieJar()            # load and save cookies to disk
handler = urllib.request.HTTPCookieProcessor(cookie)  # handle HTTP cookie
opener = urllib.request.build_opener(handler)         #  
urllib.request.install_opener(opener)                 # 

pp = pprint.PrettyPrinter(indent=4, depth=3)          # pretty printer


# argument parsers 
# arg_parser = argparse.ArgumentParser(description = 'thutodo') # argument parser
# # arg_parser.add_argument('--semester', help = 'semester')
# arg_parser.add_argument('--course', help = 'course')
# arg_parser.add_argument('--homework', help = 'homework')
# arg_parser.add_argument('--wj', help = 'unsubmitted homework', action="store_true")
# arg_parser.add_argument('--yj', help = 'submitted homework', action="store_true")
# arg_parser.add_argument('--yp', help = 'graded homework', action="store_true")
# args = arg_parser.parse_args()

def request_page(request_url, data={}):
  ''' handle url request'''
  post_data = urllib.parse.urlencode(data).encode() if data else None
  request_url = request_url if request_url.startswith('http') else url + request_url
  request = urllib.request.Request(request_url, post_data, request_headers)
  # print(request_url)

  try: 
    # response = opener.open(request)
    response = urllib.request.urlopen(request)
    return response.read().decode('utf-8')
  except urllib.error.URLError as e:
    print(request_url, e.code, ':', e.reason)
  except Exception as e:
    print(e, request_url)

def load_json(request_url, data={}): 
  '''decode json object'''
  try: 
    page = request_page(request_url, data)
    page_json = json.loads(page)
    return page_json
  except Exception as e:
    print(e)
    return {}

def download():
  '''download files'''

def load_courses():
    try:
      # information about this semester
      current_and_next_semester = load_json('/b/kc/zhjw_v_code_xnxq/getCurrentAndNextSemester')['result']
      current_semester = current_and_next_semester['xnxqmc']
      start_semester_date = current_and_next_semester['kssj']
      end_semester_date = current_and_next_semester['jssj']
      semester_id = current_and_next_semester['xnxq']
      print("本学期: ", semester_id, current_semester, start_semester_date, "到", end_semester_date)

      courses = []
      # load this semester's courses' info
      try: 
        courses = load_json('/b/wlxt/kc/v_wlkc_xs_xkb_kcb_extend/student/loadCourseBySemesterId/' + semester_id)['resultList'] # + '/0?timestamp=' + calender.timegm(time.gmtime()))
      except Exception as e:
        print(e) 
      return courses

    except:
      print("休学？退学？")
      return []

def login(username, password):
  # api
  request_url = 'https://id.tsinghua.edu.cn/do/off/ui/auth/login/post/bb5df85216504820be7bba2b0ae1535b/0?/login.do'
  data = {
    'i_user' : username, 
    'i_pass' : password,
    'atOnce' : 'true'
  }

  # make request and return page html
  page = request_page(request_url, data)

  # see if request is successful
  successful = 'SUCCESS' in page
  if successful:
    print(username, "登入成功")
  else:
    print(username, "登入失败")

  # if successsful redirect to correct url
  if successful:
    # login success
    redirect_url = page.split('replace("')[2].split('");\n')[0] 
    # redirect with ticket, sends to student page
    redirect_page = request_page(request_page(redirect_url).split('location="')[1].split('";\r\n')[0])
    # print(redirect_page)
  return successful

def append_hw_csv(file_name, hw):
  csv_content = []

  try: 
    csv_content = [i for i in csv.reader(open(file_name)) if i]
  except:
    csv_content = [['课程名字', '作业', '说明', '生效日期', '截止日期', '状态']]

  current_time = str(datetime.datetime.now()).split('.')[0]
  hw_info = [hw['kcm'], hw['bt'], hw['description'], hw['kssjStr'], hw['jzsjStr'], '0']

  if hw_info[0:5] not in [entry[0:5] for entry in csv_content] and current_time < hw['jzsjStr'] :
    # hw_info = [*hw_info[0:5], *["0"]]
    csv_content.append(hw_info)
    try: 
      csv.writer(open(file_name, 'w', newline='')).writerows(csv_content)
    except UnicodeEncodeError as e:
      print(e)
      csv_content = [[entry.replace(u'\xa0', u' ') for entry in row] for row in csv_content]
      csv.writer(open(file_name, 'w', newline='')).writerows(csv_content)
     
def load_hw(username, course):
  # create hw folder
  curr_direct = os.getcwd() 
  curr_direct_hw = os.path.join(course['kcm'], '作业')
  if not os.path.exists(curr_direct_hw):
    os.makedirs(curr_direct_hw)

  # data = {'aoData': [{"name": "wlkcid", "value": course['wlkcid']}]}
  data = { 'wlkcid': course['wlkcid'], 'size' : '' }
  hw_types = ['zyListWj', 'zyListYjwg', 'zyListYpg']

  # load all hw for course
  hws = []
  try:
      hws = load_json("/b/wlxt/kczy/zy/student/index/" + hw_types[0], data)['object']['aaData']
      # hws = load_json("/b/wlxt/kczy/zy/student/" + hw_types[1], data)['object']['aaData']
  except Exception as e:
    print(e) 

  print("没交的作业", len(hws))

  # append all hw to csv
  csv_folder = os.path.join('','csv')
  if not os.path.exists(csv_folder):
    os.makedirs(csv_folder)
  for hw in hws:
    hw['kcm'] = course['kcm'] 
    hw_page = bs(request_page('/f/wlxt/kczy/zy/student/viewCj?wlkcid=%s&zyid=%s&xszyid=%s' % (hw['wlkcid'], hw['zyid'], hw['xszyid'])), 'html.parser')
    # if homework has a description
    hw_page_description = hw_page.find_all('div', class_='list calendar clearfix')[0].findChild('p')
    hw["description"] = ""
    if hw_page_description is not None:
      hw["description"] = hw_page_description.text.replace(u'\xa0', u' ')
      

    append_hw_csv(os.path.join(csv_folder, 'unsubmitted.csv'), hw)

def append_announcements_csv(file_name, announcement):
  '''append the announcements csv'''
  csv_content = []

  try: 
    csv_content = [i for i in csv.reader(open(file_name)) if i]
  except:
    csv_content = [['课程名字', '公告', '公告描述', '发布时间', '状态']]

  # print(announcement)
  announcement_info = [announcement['wlkcid'], announcement['title'], announcement['description'], announcement['post_date'], '0']
  
  current_time = str(datetime.datetime.now()).split('.')[0]

  if announcement_info[0:5] not in [entry[0:5] for entry in csv_content]:
    csv_content.append(announcement_info)
    try: 
      csv.writer(open(file_name, 'w', newline='')).writerows(csv_content)
    except UnicodeEncodeError as e:
      # encoding error for character '\xa0'
      csv_content = [[entry.replace(u'\xa0', u' ') for entry in row] for row in csv_content]
      csv.writer(open(file_name, 'w', newline='')).writerows(csv_content)

def load_announcements(username, course):
  '''load new announcements from learn'''
  url = "/b/wlxt/kcgg/wlkc_ggb/student/pageListXs"
  data = {
    'aoData' : [
      {"name":"sEcho","value":1},
      {"name":"iColumns","value":3},
      {"name":"sColumns","value":",,"},
      {"name":"iDisplayStart","value":0},
      {"name":"iDisplayLength","value":"30"},
      {"name":"mDataProp_0","value":"bt"},
      {"name":"bSortable_0","value":True},
      {"name":"mDataProp_1","value":"fbr"},
      {"name":"bSortable_1","value":True},
      {"name":"mDataProp_2","value":"fbsj"},
      {"name":"bSortable_2","value":True},
      {"name":"iSortingCols","value":0},
      {"name":"wlkcid","value": course['wlkcid']}
    ]
  }

  announcements = []
  try:
    announcements_json = load_json(url, data)
    announcements_list = announcements_json['object']['aaData']


    remove = ['&lt;p&gt;', '&lt;/p&gt;', '&lt;/li&gt;', '&lt;li&gt;', '&amp;nbsp;', '&lt;ul&gt;', '\n' ]
    remove = ",".join(map(str,remove))
    announcements = [{
      'title' : entry['bt'], 
      'description' : entry['ggnrStr'].translate(str.maketrans('', '', remove)) if '成绩' not in entry['bt'] and entry['ggnrStr'] is not None else '',
      'post_date' : entry['fbsj'], 
      'sfqd': entry['sfqd'], 
      'sfyd' : entry['sfyd'],
      'wlkcid' : entry['wlkcid']
      }
    for entry in announcements_list if entry['bt'] != '' ]
  
    # print(announcements)
  except Exception as e:
    print(e);

  print("公告个数", len(announcements))
  csv_folder = os.path.join('','csv')

  for announcement in announcements:  
    append_announcements_csv(os.path.join(csv_folder, 'announcements.csv'), announcement)

def load_documents(username, course):
  '''load class materials from learn'''

def main():
  # handle batch arguments
  if len(sys.argv) > 1 :
    print(len(sys.argv))
    username = str(sys.argv[1])
    password = str(sys.argv[2])
  # username and password
  else:
    username = input('请输入INFO账号: ')
    password = getpass.getpass('请输入INFO密码: ')

  login_status = login(username, password)

  # if login succcessful
  if login_status: 
    courses = load_courses()
    # print("本学期的课程和课程信息")
    # for course in courses:
      # print(course)
      # print(course['kcm'], course['kch'] + "-" + course['kxhnumber'], course['ywkcm'])

    # make course folder, sync course information. homework
    for course in courses:
      print('syncing', course['kcm'])
      # course folders feature to store relative documents
      if not os.path.exists(course['kcm']):
        os.makedirs(course['kcm'])

      load_hw(username, course)
      load_announcements(username, course)

  print("learn.py完成")

if __name__ == '__main__':
  main()