#!/usr/bin/python

""" 
  An example using python requests and queue
  
  requirements:
  pip install logging requests 
"""

import sys
import time
import logging
import requests
from threading import Thread
# Support python 2-3 Queue
if sys.version[0] == '2':
  import Queue as queue
else:
  import queue as queue

logger = None

def setup_logging(filename):
  " Setup a console thread-safe logger "

  global logger

  logging.basicConfig(
    filename=filename,
    filemode='w',
    format='%(asctime)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO
  )
  logger = logging.getLogger(filename)
  logger.addHandler(logging.StreamHandler())

def nonthreadfunction(f):
  " HTTP Request "

  logger.info("Sending {}".format(f))
  res = requests.get(f)

  return res

def threadfunction(q, data):
  " Execute the queue "

  while not q.empty():
    # queue not empty
    f = q.get()
    res = nonthreadfunction(f)
    q.task_done()
    data.append(res.content)
  
  return data

def threadstart(tasks, thread_count):
  " Start the thread pool "

  data = []
  q = queue.Queue()

  for task in tasks:
    q.put(task)
  for i in range(0,  thread_count):
    t = Thread(target=threadfunction, args=(q, data))
    t.daemon = True
    t.start()
  q.join()

  return data

def queueexample():
  " Execute nonthreadfunction as multithreadfunction"

  print("[+] Starting Example")
  setup_logging('queue-example.log')
  tasks = ["http://httpbin.org/get?id={}".format(i) for i in range(0, 50)]

  # NonThreadFunction(Threads=1)
  start_time = time.time()
  data = []
  for j in tasks:
    result = nonthreadfunction(j)
    data.append(result)
  print("1 Threads --- %s seconds ---" % (time.time() - start_time))
  # ThreadFunction(Threads=5)
  start_time = time.time()
  thread_count = 5
  data = threadstart(tasks, thread_count)
  print("5 Threads --- %s seconds ---" % (time.time() - start_time))
  # ThreadFunction(Threads=15)
  start_time = time.time()
  thread_count = 15
  data = threadstart(tasks, thread_count)
  print("15 Threads --- %s seconds ---" % (time.time() - start_time))

queueexample()
