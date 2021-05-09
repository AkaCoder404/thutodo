# README.md

hello this is readme for automatic task downloader for thu webpage, and uploader to dida todo list application

this is split into two parts, learn.py and dida.py

## Learn.py
Takes user's username and password as inputs and logs onto learn.tsinghua.edu.cn to get the current homework list of this semester. The applciation parses each classes unsubmitted homework list and retrieves its name, description, the date assigned, and the date due and outputs it to csv/unsubmmitted.csv

## Dida.py
Takes user's username and password for dida365.com and uploads the upcoming homework tasks in csv/unsubmmitted and uploads it to dida365. So far, it only uploads to the homework group, so make sure there is a homework group.

task
1. more possible functionality using command line args, argparse
  - download hw files to correct folder
  - download class materials to correct folder
  - choose what class specifically to update
2. create dida365 homework group if it currently doesn't exist
completed
1. login learn.tsinghua.edu.cn
2. create folders for each course
3. append csv with unsubmmited hw information
4. login to dida
5. upload task to dida
6. prevent same tasks from being added/uploaded after completion by updating csv
7. automate bat script for input
