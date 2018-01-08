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
	# MAS數量 0
	trash, num_MAS = splunkQuery(service, "search * host=MAS | stats count(host)", timeRange, "MAS數量")
	num_MAS = res2val(num_MAS)

	# SIM數量 1
	trash, num_SIM = splunkQuery(service, "search * host=SIM | stats count(host)", timeRange, "SIM數量")
	num_SIM = res2val(num_SIM)

	# MAS -DNS逐日統計表 2
	trash, countDaily_DNS_MAS = splunkQuery(service, "search * host=MAS| timechart count span=1d by host", timeRange, "MAS -DNS逐日統計表")
	countDaily_DNS_MAS = orderDict2df(countDaily_DNS_MAS, 0)

	# MAS -惡意DN查詢逐日統計表 3
	trash, dailySearchStat_DN_MAS = splunkQuery(service, "search * host=MAS | timechart count span=1d limit=20 by url", timeRange, "MAS -惡意DN查詢逐日統計表")
	dailySearchStat_DN_MAS = orderDict2df(dailySearchStat_DN_MAS, 0)

	# MAS -10大惡意DN查詢資訊 - Table & Figure 4
	trash, top10_DN_searchInfo_MAS = splunkQuery(service, "search * host=MAS | stats count by url | sort limit=10 -count", timeRange, "MAS -10大惡意DN查詢資訊")
	top10_DN_searchInfo_MAS = orderDict2df(top10_DN_searchInfo_MAS, 0)

	# MAS -查詢惡意DN之10大來源主機 - Table & Figure 5
	trash, top10_DN_server_MAS = splunkQuery(service, "search * host=MAS | stats count by src | sort limit=10 -count", timeRange, "MAS -查詢惡意DN之10大來源主機")
	top10_DN_server_MAS = orderDict2df(top10_DN_server_MAS, 0)
	
	# MAS -觸發惡意DN查詢資訊之來源主機Top 10統計列表 6
	trash, top10_triggerDN_searchInfo_MAS = splunkQuery(service, "search * host=MAS | stats count by src,url | sort limit=10 -count", timeRange, "觸發惡意DN查詢資訊之來源主機Top 10統計列表")
	top10_triggerDN_searchInfo_MAS = orderDict2df(top10_triggerDN_searchInfo_MAS, 0)

	# SIM -觸發事件逐日統計表 7
	trash, trigger_event_stat_SIM = splunkQuery(service, "search * host=SIM | timechart count span=1d limit=20 by rule", timeRange, "觸發事件逐日統計表")
	trigger_event_stat_SIM = orderDict2df(trigger_event_stat_SIM, timeRange)

	# SIM -高威脅性惡意程式類型事件之Top 10數量 8
	trash, top10_highPoMalwareEvent_SIM = splunkQuery(service, 'search * host=SIM "*(HTM)*" | stats count by rule | sort limit=10 -count', timeRange, "SIM -高威脅性惡意程式類型事件之Top 10數量")
	top10_highPoMalwareEvent_SIM = orderDict2df(top10_highPoMalwareEvent_SIM, 0)

	# SIM -觸發高威脅性惡意軟體類型事件之來源主機Top 10數量 9
	trash, top10_highPoMalwareEventServer_SIM = splunkQuery(service, 'search * host=SIM "*(HTM)*" | stats count by src,rule | sort limit=10 -count', timeRange, "觸發高威脅性惡意軟體類型事件之來源主機Top 10數量")
	top10_highPoMalwareEventServer_SIM = orderDict2df(top10_highPoMalwareEventServer_SIM, 0)

	# SIM -DN類型惡意中繼站事件之Top 10數量 10
	trash, top10_interEvent_DN_SIM = splunkQuery(service, 'search * host=SIM "Suspicious host name*" | stats count by rule | sort limit=10 -count', timeRange, "SIM -DN類型惡意中繼站事件之Top 10數量")
	top10_interEvent_DN_SIM = orderDict2df(top10_interEvent_DN_SIM, 10)

	# SIM -IP類型惡意中繼站事件之Top10數量 11
	trash, top10_interEvent_IP_SIM = splunkQuery(service, 'search * host=SIM "Suspicious ip*" | stats count by rule | sort limit=10 -count', timeRange, "SIM -IP類型惡意中繼站事件之Top10數量")
	top10_interEvent_IP_SIM = orderDict2df(top10_interEvent_IP_SIM, 10)

	# SIM 觸發DN類型惡意中繼站事件之來源主機Top 10數量 12
	trash, top10_triggerInterEvent_DN_SIM = splunkQuery(service, 'search * host=SIM NOT (src=“140.92.66.71” OR src=“140.92.66.74” OR src=“140.92.66.75” OR src=“140.92.66.45” OR src=“140.92.13.39” OR src=“140.92.13.40” OR src=“140.92.13.41” OR src=“140.92.13.42” OR src=“140.92.13.43” OR src=“140.92.13.44” OR src=“140.92.13.45” OR src=“118.163.123.115” OR src="140.92.100.243" ) "Suspicious host name*" | stats count by src, rule | sort limit=10 -count', timeRange, "SIM 觸發DN類型惡意中繼站事件之來源主機Top 10數量")
	top10_triggerInterEvent_DN_SIM = orderDict2df(top10_triggerInterEvent_DN_SIM, 10)

	# SIM -觸發IP類型惡意中繼站事件之來源主機Top 10數量 13
	trash, top10_triggerInterEvent_IP_SIM = splunkQuery(service, 'search * host=SIM NOT (src="140.92.66.71" OR src="140.92.66.74" OR src="140.92.66.75" OR src="140.92.66.45") "Suspicious ip*" | stats count by src,rule | sort limit=10 -count', timeRange, "SIM -觸發IP類型惡意中繼站事件之來源主機Top 10數量")
	top10_triggerInterEvent_IP_SIM  = orderDict2df(top10_triggerInterEvent_IP_SIM, 10)

	# 外對內歸則觸發TOP10 14
	trash, top10_out2inRule_trigger = splunkQuery(service, 'search * host=SIM dst=140.92.* NOT src=140.92.* | stats count by rule | sort limit=10 -count aesc', timeRange, "外對內歸則觸發TOP10")
	top10_out2inRule_trigger = orderDict2df_from4(top10_out2inRule_trigger)

	# 內對外規則觸發TOP10 15
	trash, top10_in2outrule_trigger = splunkQuery(service, 'search * host=SIM src=140.92.* NOT dst=140.92.* | stats count by rule | sort limit=10 -count aesc', timeRange, "內對外規則觸發TOP10")
	top10_in2outrule_trigger = orderDict2df_from4(top10_in2outrule_trigger)

	print "=== All necessary data have been already exported!!! ===\n"

	return [num_MAS, num_SIM, countDaily_DNS_MAS, dailySearchStat_DN_MAS, top10_DN_searchInfo_MAS , top10_DN_server_MAS, top10_triggerDN_searchInfo_MAS, trigger_event_stat_SIM, top10_highPoMalwareEvent_SIM, top10_highPoMalwareEventServer_SIM, top10_interEvent_DN_SIM, top10_interEvent_IP_SIM, top10_triggerInterEvent_DN_SIM, top10_triggerInterEvent_IP_SIM, top10_out2inRule_trigger, top10_in2outrule_trigger]


# ==========================================================================
# ================ function below is only for autoGenDoc ===================
# ==========================================================================


def orderDict2str(orderDict):
	# this function is used to get the values from ordered dict data 
	# format, and transfers into int format.
	val = orderDict.values()[0]
	return val

def queryData4(service, search_ip, timeRange):
	# 事件觸發單位
	trash, EventTriggerDept_III = splunkQuery(service, 'search * host=SIM  src="' + search_ip + '" | lookup checkip subnet as src OUTPUT dept | stats values(dept)', timeRange, "事件觸發單位")
	EventTriggerDept_III = orderDict2str(EventTriggerDept_III[0])

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

	print "=== All necessary data have been already exported!!! ===\n"

	return [EventTriggerDept_III, searchPeriodTriggerEvent_III, searchPeriodAttackEvent_III, EventDiary_III]







