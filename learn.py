# -*- coding: utf-8 -*-

# imports
import getpass # obscure text on terminal
import argparse # parser for command line options 
import json 
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
arg_parser = argparse.ArgumentParser(description = 'thutodo') # argument parser
# arg_parser.add_argument('--semester', help = 'semester')
arg_parser.add_argument('--course', help = 'course')
arg_parser.add_argument('--homework', help = 'homework')
arg_parser.add_argument('--download', help = 'download')
arg_parser.add_argument('--wj', help = 'unsubmitted homework', action="store_true")
arg_parser.add_argument('--yj', help = 'submitted homework', action="store_true")
arg_parser.add_argument('--yp', help = 'graded homework', action="store_true")

args = arg_parser.parse_args()

def request_page(request_url, data={}):
  post_data = urllib.parse.urlencode(data).encode() if data else None
  # make request
  request = urllib.request.Request(request_url if request_url.startswith('http') else url + request_url, post_data, request_headers)
  
  try: 
    # response = opener.open(request)
    response = urllib.request.urlopen(request)
    return response.read().decode('utf-8')
  except urllib.error.URLError as e:
    print(request_url, e.code, ':', e.reason)
  except Exception as e:
    print(e, request_url)   
  
def load_json(request_url, data={}): 
    try: 
      page = request_page(request_url, data)
      page_json = json.loads(page)
      return page_json
    except Exception as e:
      print(e)
      return {}

def download_resource():
  print("downloading")
  # filename = escape(name)
  # if os.path.exists(filename) and os.path.getsize(filename) or 'Connection__close' in filename:
  #     return
  # try:
  #     with TqdmUpTo(ascii=True, dynamic_ncols=True, unit='B', unit_scale=True, miniters=1, desc=filename) as t:
  #         urllib.request.urlretrieve(url + uri, filename=filename, reporthook=t.update_to, data=None)
  # except:
  #     print('Could not download file %s ... removing broken file' % filename)
  #     if os.path.exists(filename):
  #         os.remove(filename)
  #     return

def append_announcement_csv():
  print("append announcement csv")

def load_announcements():
  print("loading announcements")

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
  data = { 'i_user' : username, 'i_pass' : password, 'atOnce' : 'true' }

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
  # print(current_time)
  
  hw_info = [hw['kcm'], hw['bt'], hw['description'], hw['kssjStr'], hw['jzsjStr'], '0']
  # print(hw_info)
  # csv_content.append(hw_info)
  if hw_info not in csv_content and current_time < hw['jzsjStr'] :
    csv_content.append(hw_info)
   
  csv.writer(open(file_name, 'w')).writerows(csv_content)

def load_hw(username, course):
  # create hw folder
  curr_direct = os.getcwd() 
  # curr_direct_hw = os.path.join(course['kcm'], '作业')
  # if not os.path.exists(curr_direct_hw):
  #   os.makedirs(curr_direct_hw)

  # data = {'aoData': [{"name": "wlkcid", "value": course['wlkcid']}]}
  data = {
    'wlkcid': course['wlkcid'],
    'size' : ''
  }
  
  ## 作业未交、作业已交，作业已批改
  hw_types = ['zyListWj', 'zyListYjwg', 'zyListYpg']

  # load all hw for course
  hws = []
  try:
      hws = load_json("/b/wlxt/kczy/zy/student/index/" + hw_types[0], data)['object']['aaData']
      # hws = load_json("/b/wlxt/kczy/zy/student/" + hw_types[1], data)['object']['aaData']
  except Exception as e:
    print(e) 

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
      hw["description"] = hw_page_description.text
      # print(hw_page_description.text)


    append_hw_csv(os.path.join(csv_folder, username + '_' + hw_types[0] + '.csv'), hw)

def main():
  # arguments
  print(args)
  # username and password
  # username = input('请输入INFO账号: ')
  # password = getpass.getpass('请输入INFO密码: ')

  username = "litq18"
  password = "huabasket66!!!!"

  login_status = login(username, password)

  # if login succcessful
  if login_status: 
    courses = load_courses()
    # info
    # print("本学期的课程和课程信息")
    # for course in courses:
    #   print(course['kcm'], course['kch'] + "-" + course['kxhnumber'], course['ywkcm'])

    # make course folder, sync course information. homework
    for course in courses:
      print('syncing', course['kcm'])
      # course folders feature to store relative documents
      if not os.path.exists(course['kcm']):
        os.makedirs(course['kcm'])

      load_hw(username, course)
    # print(courses[0]['kcm'])
    # load_hw(courses[0])

if __name__ == '__main__':
  main()