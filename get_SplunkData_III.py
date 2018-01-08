#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
# this code is used to get the raw data from the splunk server, in addition, 
# it also automatically generate the same figures as the presentation from 
# website UI.
# caution: this code is written by Python 2.7.13
# 
# coded by Chan, Chun-Hsiang @ III, Taipei 20171206
# 
# version: splunkSearchCode.v.20171206001

# import packages
import splunklib.client as client
import splunklib.results as results
from collections import OrderedDict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import os
import pickle
from splunkSearchFunc_III import *

# basic setting
HOST = "YOUR IP"
PORT = "YOUR PORT"
USERNAME = 'YOUR USERNAME'
PASSWORD = 'YOUR PASSWORD'
timeRange = {"earliest_time": "2017-12-01T00:00:00.000",
                  "latest_time": "2017-12-10T23:59:00.000"}
filename = 'testdata_iii.pkl'

# connect to server
service = Connect2Server(HOST, PORT, USERNAME, PASSWORD)

# fetch data
data = allValues(service, timeRange)

# save data into pickle
with open(filename, 'wb') as f:
    pickle.dump(data, f)

# done message
print "All data have been exported and saved into local depository!!!\n"