#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
# this file lists all function for fetch necessary data from the MongoDB server.
# 
# caution: this code is written by Python 2.7.13
# 
# coded by Chan, Chun-Hsiang @ III, Taipei 20180108
# 
# version: autoGeneventDoc_funclist_mongo.v.20180108001

# import packages
import pandas as pd
import numpy as np
import timeit
import datetime
import os
import pymongo
from pymongo import MongoClient
import re

# self-define function
# get MongoDB data via date information (year and month)
def get_dataByDateMonth(db, year, month, db_name):
    regx = re.compile(year + "-" + month + "-*")
    if db_name == 'iii':
        res = db.iii_event.find({"date":{'$regex': regx}})
    elif db_name == 'ites':
        res = db.ites_event.find({"date":{'$regex': regx}})
    listResults = []
    for doc in res:
        listResults.append(doc)
    resDF = pd.DataFrame.from_dict(listResults)
    print('MongoDB Data has successfully exported to dataframe from MongoDB via get_dataByDateMonth!\n')
    return resDF

# get MongoDB data via date information (year, month and day)
def get_dataByDateMonthDay(db, year, month, day, db_name):
    regx = re.compile(year + "-" + month + "-" + day)
    if db_name == 'iii':
        res = db.iii_event.find({"date":{'$regex': regx}})
    elif db_name == 'ites':
        res = db.ites_event.find({"date":{'$regex': regx}})
    listResults = []
    for doc in res:
        listResults.append(doc)
    resDF = pd.DataFrame.from_dict(listResults)
    print('MongoDB Data has successfully exported to dataframe from MongoDB via get_dataByDateMonthDay!\n')
    return resDF

# get MongoDB data via event id information
def get_dataByEventID(db, event_id, db_name):
    regx = re.compile(event_id)
    if db_name == 'iii':
        res = db.iii_event.find({"event_id":{'$regex': regx}})
    elif db_name == 'ites':
        res = db.ites_event.find({"event_id":{'$regex': regx}})
    listResults = []
    for doc in res:
        listResults.append(doc)
    resDF = pd.DataFrame.from_dict(listResults)
    print('MongoDB Data has successfully exported to dataframe from MongoDB via get_dataByEventID!\n')
    return resDF

# get source IP in order to run next step "splunk data collection"
def get_srcIP_info(ip_col):
    # ip regex
    ValidIpAddressRegex = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$";
    # ip: series to string; then, split by ' '(blank)
    IP_info = str(ip_col)
    IP_info = IP_info.split(' ')
    # reread valid ip info again
    IP_data = []
    for i in range(len(IP_info)):
        tmp = re.findall(ValidIpAddressRegex, IP_info[i])
        if len(tmp)!=0:
            IP_data.append(tmp[0])
    return IP_data