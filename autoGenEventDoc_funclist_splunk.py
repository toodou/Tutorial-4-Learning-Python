#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
# this file lists all function for fetch necessary data from the Splunk server.
# 
# caution: this code is written by Python 2.7.13
# 
# coded by Chan, Chun-Hsiang @ III, Taipei 20180108
# 
# version: autoGeneventDoc_funclist_splunk.v.20180108001

# import packages
import splunklib.client as client
import splunklib.results as results
from collections import OrderedDict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import os

# decode list contents
def decodeList_2_UTF8(mylist):
    for i in xrange(len(mylist)):
        if str(type(mylist[i]))=="<type 'list'>":
#             print i, 'i am list'
            mylist[i] = [x.decode('UTF8') for x in mylist[i]]
        else:
#             print i, 'i am not str'
            ss = str(mylist[i])
            mylist[i] = ss.decode("utf-8")
    return mylist

# merge cell of the table in the MS Word
def cellMerge(table_obj, S_coor_xy, E_coor_xy):
    for i in xrange(S_coor_xy[1], E_coor_xy[1]):
        a = table_obj.cell(S_coor_xy[0], S_coor_xy[1])
        b = table_obj.cell(E_coor_xy[0], i)
        C = a.merge(b)
    return C

# merge row of the table in the MS Word
def rowMerge(table_obj, S_coor_xy, E_coor_xy):
    for i in xrange(S_coor_xy[0], E_coor_xy[0]):
        a = table_obj.cell(S_coor_xy[0], S_coor_xy[1])
        b = table_obj.cell(S_coor_xy[0]+i, E_coor_xy[1])
        C = a.merge(b)
    return C

# connect to the splunk server
def Connect2Server(HOST, PORT, USERNAME, PASSWORD):
	# this function is used to connect to the splunk server via server 
	# connection settings, including host, port, username, password.
	# if it run without any errors, then it will return a message to 
	# tell you that the job is successfully completed.
    service = client.connect(
		host = HOST,
		port = PORT,
		username = USERNAME,
		password = PASSWORD)
    print "You have successfully connected to the splunk server!\n"
    return service

# set the splunk query
def splunkQuery(service, searchCommand, timeRange, jobTitle):
	# this funciton is used to request raw data from the splunk server 
	# via your specified query command. when the job is done, it will
	# automatically generate a meesage to tell you that the job has 
	# successfully completed.
	searchquery_oneshot = searchCommand
	kwargs_oneshot = timeRange
	oneshotsearch_results = service.jobs.export(searchquery_oneshot, ** kwargs_oneshot)
	data = []
	reader = results.ResultsReader(oneshotsearch_results)
	for item in reader:
	    data.append(item)
	print jobTitle + " search has been successfully done!\n"
	return reader, data

# get datetime information via the variable called "timeRange"
def get_dateInfo(timeRange):
	# this function is used to split the timeRange (for query) into 
	# integel data format, then combines the start time and end time
	# into single list.
    t_list = []
    for i in range(2):
        YYYY = int(timeRange.values()[i][0:4])
        MM = int(timeRange.values()[i][5:7])
        DD = int(timeRange.values()[i][8:10])
        hh = int(timeRange.values()[i][11:13])
        mm = int(timeRange.values()[i][14:16])
        ss = int(timeRange.values()[i][17:19])
        t = datetime.datetime(YYYY, MM, DD, hh, mm, ss)
        t_list.append(t)
    return t_list

# get the datetime period from the variable timeRange
def get_datePeriod(timeRange):
	# this function is used to get the date period in DAY resolution. 
    t_list = get_dateInfo(timeRange)
    time1 = t_list[0]
    time2 = t_list[1]
    elapsedTime = time2 - time1
    dev_days = abs(elapsedTime.days)
    return dev_days

# transfer the orderdict to string
def orderDict2str(orderDict):
	# this function is used to get the values from ordered dict data 
	# format, and transfers into int format.
	val = orderDict.values()[0]
	return val

# transfer the orderdict to pandas dataframe
def orderDict2df(orderDict, timeRange):
	# this function is used to get the raw data from the ordered dict
	# via analyzing the data structure inside the dict, and then expor
	# all correct information to the pandas dataframe.
	for i in range(len(orderDict)):
		if str(type(orderDict[i]))!="<class 'splunklib.results.Message'>":
			break
	ind = i
	key = orderDict[ind].keys()
	df = pd.DataFrame(columns=key)

	if timeRange!=0 and str(type(timeRange))!="<type 'dict'>":
		dd=timeRange
	elif str(type(timeRange))=="<type 'int'>":
		dd = len(orderDict)-ind
	else:
		dd = get_datePeriod(timeRange)
		readdataStart =len(orderDict)-dd

	datatypelist = []
	for i in range(len(orderDict)):
		dtype_i = str(type(orderDict[i]))
		if dtype_i == "<class 'splunklib.results.Message'>":
			isdata = 0
		else:
			isdata = 1
		datatypelist.append(isdata)
	for i in reversed(xrange(len(datatypelist))):
		if datatypelist[i]==0:
			readdataStart = i+1
			break

	for i in range(readdataStart, len(orderDict)):
		tmp_df = pd.DataFrame([orderDict[i].values()], 
                   columns=orderDict[i].keys())
		df = df.append(tmp_df, ignore_index=True)
	df = df.replace(np.nan, 0, regex=True)
	return df

# query data for automatically generating event document
def queryData4(service, search_ip, timeRange, db_name):
	if db_name == 'iii':
		# 事件觸發單位
		trash, EventTriggerDept_III = splunkQuery(service, 'search * host=SIM  src="' + search_ip + '" | lookup checkip subnet as src OUTPUT dept | stats values(dept)', timeRange, "事件觸發單位")
		EventTriggerDept_III = orderDict2str(EventTriggerDept_III[len(EventTriggerDept_III)-1])

		# 查詢期間觸發事件一覽
		trash, searchPeriodTriggerEvent_III = splunkQuery(service, 'search * host=SIM (src="' + search_ip + '")  | timechart count span=1h by rule', timeRange, "查詢期間觸發事件一覽")
		searchPeriodTriggerEvent_III = orderDict2df(searchPeriodTriggerEvent_III, 0)

		# 查詢期間攻擊事件趨勢
		trash, searchPeriodAttackEvent_III = splunkQuery(service, 'search * host=SIM (src="' + search_ip + '") | chart sparkline count by rule | sort - count aesc | rename rule as 規則名稱 | rename sparkline as 事件頻率 | rename count as 數量  | sort limit=5 -count', timeRange, "查詢期間攻擊事件趨勢")
		searchPeriodAttackEvent_III = orderDict2df(searchPeriodAttackEvent_III, 0)
		searchPeriodAttackEvent_III = list(searchPeriodAttackEvent_III['規則名稱'])

		# 事件日誌
		trash, EventDiary_III = splunkQuery(service, 'search * host=SIM (src="' + search_ip + '") | sort limit=10 -count', timeRange, "事件日誌")
		EventDiary_III = orderDict2df(EventDiary_III, 0)
		EventDiary_III = list(EventDiary_III._raw)

	elif db_name == 'ites':
		# 查詢期間觸發事件一覽
		trash, searchPeriodTriggerEvent_III = splunkQuery(service, 'search * host=ITES ' + search_ip + '  | timechart count limit=30 span=1h by rule', timeRange, "查詢期間觸發事件一覽")
		searchPeriodTriggerEvent_III = orderDict2df(searchPeriodTriggerEvent_III, 0)

		# 查詢期間攻擊事件趨勢
		trash, searchPeriodAttackEvent_III = splunkQuery(service, 'search * host=ITES ' + search_ip + ' | chart sparkline count by rule | sort - count aesc | rename rule as 規則名稱 | rename sparkline as 事件頻率 | rename count as 數量', timeRange, "查詢期間攻擊事件趨勢")
		searchPeriodAttackEvent_III = orderDict2df(searchPeriodAttackEvent_III, 0)
		searchPeriodAttackEvent_III = list(searchPeriodAttackEvent_III['規則名稱'])

		# 事件日誌
		trash, EventDiary_III = splunkQuery(service, 'search * host=ITES ' + search_ip + ' | sort limit=10 -count', timeRange, "事件日誌")
		EventDiary_III = orderDict2df(EventDiary_III, 0)
		EventDiary_III = list(EventDiary_III._raw)
	print "=== All necessary data have been already exported!!! ===\n"

	if db_name == 'iii': 
		return [EventTriggerDept_III, searchPeriodTriggerEvent_III, searchPeriodAttackEvent_III, EventDiary_III]
	elif db_name == 'ites':
		return [searchPeriodTriggerEvent_III, searchPeriodAttackEvent_III, EventDiary_III]
