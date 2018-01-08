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
# version: splunkSearchCode.v.20171213001

# import packages
import splunklib.client as client
import splunklib.results as results
from collections import OrderedDict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import os

# global variable definition

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
    print "you have successfully connected to the splunk server!\n"
    return service

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

def get_datePeriod(timeRange):
	# this function is used to get the date period in DAY resolution. 
    t_list = get_dateInfo(timeRange)
    time1 = t_list[0]
    time2 = t_list[1]
    elapsedTime = time2 - time1
    dev_days = abs(elapsedTime.days)
    return dev_days

def orderDict2int(orderDict):
	# this function is used to get the values from ordered dict data 
	# format, and transfers into int format.
	val = orderDict.values()[0]
	val = int(val)
	return val

def res2val(res):
	# this function is used to get the values from ordered dict into
	# int format. (only for single value output)
	res = res[len(res)-1]
	res = orderDict2int(res)
	return res

def orderDict2df(orderDict, timeRange):
	# this function is used to get the raw data from the ordered dict
	# via analyzing the data structure inside the dict, and then expor
	# all correct information to the pandas dataframe.
	for i in range(len(orderDict)):
		if str(type(orderDict[i]))!="<class 'splunklib.results.Message'>":
			ind = i
			break
		elif i==len(orderDict)-1:
			ind = 'No data have been found!'
			print ind
			break

	if ind!='No data have been found!':
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
	else:
		df = 'No data have been found!'
	return df

def orderDict2df_from4(orderDict):
	# this function is used to get the raw data from the ordered dict
	# via analyzing the data structure inside the dict, and then expor
	# all correct information to the pandas dataframe.
	for i in range(len(orderDict)):
		if str(type(orderDict[i]))!="<class 'splunklib.results.Message'>":
			ind = i
			break
	key = orderDict[ind].keys()
	df = pd.DataFrame(columns=key)

	for i in range(len(orderDict)-10, len(orderDict)):
		tmp_df = pd.DataFrame([orderDict[i].values()], 
                   columns=orderDict[i].keys())
		df = df.append(tmp_df, ignore_index=True)
	df = df.replace(np.nan, 0, regex=True)
	return df

def allValues(service, timeRange):
	# this function is used to query all necessary data for III month 
	# report and export to a single pickle file.
	# 本月事件總量
	trash, num_event = splunkQuery(service, "search host=ITES| stats count(host)", timeRange, "本月事件總量")
	num_event = res2val(num_event)

	# 事件規則類型比例
	trash, eventRuleTypeRatio = splunkQuery(service, "search host=ITES | stats count by class", timeRange, "事件規則類型比例")
	eventRuleTypeRatio = orderDict2df(eventRuleTypeRatio, 0)

	# 事件規則名稱比例
	trash, eventRuleNameRatio = splunkQuery(service, "search host=ITES | stats count by rule", timeRange, "事件規則名稱比例")
	eventRuleNameRatio = orderDict2df(eventRuleNameRatio, 0)

	# 事件來源位址比例
	trash, eventSourceIPRatio = splunkQuery(service, "search host=ITES | stats count by src", timeRange, "事件來源位址比例")
	eventSourceIPRatio = orderDict2df(eventSourceIPRatio, 0)

	# 事件目標位址比例 (排除140.92.0.0/16)
	trash, eventTargetIPRatio = splunkQuery(service, "search host=ITES NOT dst=140.92.* | stats count by dst", timeRange, "事件目標位址比例 (排除140.92.0.0/16)")
	eventTargetIPRatio = orderDict2df(eventTargetIPRatio, 0)
	
	# 觸發事件量逐日統計表(TOP20)
	trash, trigger_eventVolDailyStat = splunkQuery(service, "search host=ITES | timechart count span=1d limit=20 by rule", timeRange, "觸發事件量逐日統計表(TOP20)")
	trigger_eventVolDailyStat = orderDict2df(trigger_eventVolDailyStat, timeRange)

	# 觸發TOP10事件來源(排除Policy類型事件)
	trash, trigger_top10eventSource = splunkQuery(service, "search host=ITES src=140.92.* NOT rule=*POLICY*  | stats count by src,dst,rule | sort by count limit=10 desc", timeRange, "觸發TOP10事件來源(排除Policy類型事件)")
	trigger_top10eventSource = orderDict2df(trigger_top10eventSource, 0)

	# 高威脅性惡意程式類型事件數量
	trash, highRiskMalwareSEVol = splunkQuery(service, 'search host=ITES rule=*(HTM)*| stats values(_time),values(src),values(dst),values(dept),count by rule | rename rule as 規則名稱 | rename values(src) as 來源位址 | rename values(dept) as 部門 | rename count as 次數 | rename values(dst) as 目標位址 | rename values(_time) as 觸發時間 | convert ctime(觸發時間) | sort by 次數 desc', timeRange, "高威脅性惡意程式類型事件數量")
	highRiskMalwareSEVol = orderDict2df(highRiskMalwareSEVol, 0)

	# DN類型惡意中繼站事件之Top 10數量
	trash, DNtypeViaEventTop10 = splunkQuery(service, 'search host=ITES src=140.92.* rule="Suspicious host name*" | stats count by rule | sort count by desc', timeRange, "DN類型惡意中繼站事件之Top 10數量")
	DNtypeViaEventTop10 = orderDict2df(DNtypeViaEventTop10, 0)

	# 觸發DN類型惡意中繼站事件之來源主機Top 10數量
	trash, trigger_DNViaESStop10 = splunkQuery(service, 'search host=ITES src=140.92.* rule="Suspicious host name*" | stats count by src,rule | sort count limit=10 by desc', timeRange, "觸發DN類型惡意中繼站事件之來源主機Top 10數量")
	trigger_DNViaESStop10 = orderDict2df(trigger_DNViaESStop10, 0)

	# IP類型惡意中繼站事件之Top 10數量
	trash, IPtypeViaEventTop10 = splunkQuery(service, 'search host=ITES src=140.92.* rule="Suspicious ip*" | stats count by rule | sort count by desc', timeRange, "觸發DN類型惡意中繼站事件之來源主機Top 10數量")
	IPtypeViaEventTop10 = orderDict2df(IPtypeViaEventTop10, 0)

	# 觸發IP類型惡意中繼站事件之來源主機Top 10數量
	trash, trigger_IPViaESStop10 = splunkQuery(service, 'search host=ITES src=140.92.* rule="Suspicious host name*" | stats count by src,rule | sort count limit=10 by desc', timeRange, "觸發DN類型惡意中繼站事件之來源主機Top 10數量")
	trigger_IPViaESStop10 = orderDict2df(trigger_IPViaESStop10, 0)

	# 封包數量
	trash, num_packet = splunkQuery(service, 'search host=SYSALERT | timechart span=1h count by interface', timeRange, "封包數量")
	num_packet = orderDict2df(num_packet, 0)

	# 頻寬變化趨勢
	trash, bandwidthVar_trend = splunkQuery(service, 'search host=SYSALERT | timechart span=1h values(rxbn) count by interface', timeRange, "頻寬變化趨勢")
	bandwidthVar_trend = orderDict2df(bandwidthVar_trend, 0)

	print "=== All necessary data have been already exported!!! ===\n"

	return [num_event, eventRuleTypeRatio, eventRuleNameRatio, eventSourceIPRatio, eventTargetIPRatio, trigger_eventVolDailyStat, trigger_top10eventSource, highRiskMalwareSEVol, DNtypeViaEventTop10, trigger_DNViaESStop10, IPtypeViaEventTop10, trigger_IPViaESStop10, num_packet, bandwidthVar_trend]










