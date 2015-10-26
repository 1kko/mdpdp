#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# coding=utf-8

from flask import Flask, render_template, request, url_for, Response
import os
from werkzeug import secure_filename
import pymongo, json
from bson import json_util
from peewee import *
from playhouse.pool import MySQLDatabase
import threading
import sys
from dateutil.parser import parse as dateParser
from datetime import datetime
import time

# sys.path.insert(0, '/home/ikko/repo/mdpdp/')
import importer
from reversediff import findCommon

connection=pymongo.MongoClient("localhost",27017)
MDPMongoDB=connection.MDP
col_behavior=MDPMongoDB.behavior
EngineDiff=connection.enginediff
col_enginediff=EngineDiff.enginediff

count=0

database = MySQLDatabase('MEDDB', **{'password': 'qwe123', 'user': 'asduser03'})


app=Flask(__name__)
app.config['UPLOAD_FOLDER']='/tmp'
app.config['CSV_FOLDER']='/home/ikko/repo/mdpdp/csv'
application=app

# with app.request_context(environ):
#     assert request.method == 'POST'

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

class MedFile(BaseModel):
    av_scan = TextField(db_column='AV_Scan')
    ctime = DateTimeField(db_column='CTIME')
    file_name = TextField(db_column='File_Name')
    file_tag = CharField(db_column='File_Tag')
    md5_key = CharField(db_column='MD5_Key', index=True)
    mdp_rule = TextField(db_column='MDP_Rule')
    report_pc_count = IntegerField(db_column='REPORT_PC_Count')
    result_number = TextField(db_column='Result_Number')
    saved_size = IntegerField(db_column='Saved_Size')
    sign_credit = IntegerField(db_column='Sign_Credit')
    virus_name = TextField(db_column='Virus_Name')
    idx = PrimaryKeyField()
    class Meta:
        db_table = 'med_file'


def medfileSearch(md5sumlist, search, sort, order, limit, offset):

	database.get_conn().ping(True)
	# print "md5sumlist:", ', '.join(md5sumlist)[0:67], "...", ', '.join(md5sumlist)[-68:]
	# print "md5sumlist count:", len(md5sumlist)
	# print "search:", search
	# print "sort:", sort
	# print "order:", order
	# print "limit:", limit
	# print "offset:", offset

	if search!=None:
		queryResult=MedFile.select().where(MedFile.md5_key.in_(md5sumlist) & \
			(\
				MedFile.md5_key.contains(search) | \
				MedFile.file_name.contains(search) | \
				MedFile.virus_name.contains(search) | \
				MedFile.file_tag.contains(search)
			)\
		)
	else:
		queryResult=MedFile.select().where(MedFile.md5_key.in_(md5sumlist))

	if sort: 
		if sort=="MD5_KEY": 
			queryColumn=MedFile.md5_key
		if sort=="FILE_NAME": 
			queryColumn=MedFile.file_name
		if sort=="RESULT_NUMBER": 
			queryColumn=MedFile.result_number
		if sort=="VIRUS_NAME": 
			queryColumn=MedFile.virus_name
		if sort=="SIGN_CREDIT": 
			queryColumn=MedFile.sign_credit
		if sort=="REPORT_PC_COUNT": 
			queryColumn=MedFile.report_pc_count
		if sort=="SAVED_SIZE": 
			queryColumn=MedFile.saved_size
		if sort=="FILE_TAG": 
			queryColumn=MedFile.file_tag
		if sort=="CTIME": 
			queryColumn=MedFile.ctime
			
		if order=="desc":
			queryResult=queryResult.order_by(queryColumn.desc())
		else:
			queryResult=queryResult.order_by(queryColumn.asc())

	# queryResult=MedFile.select().where(MedFile.md5_key.in_(md5sumlist)).limit(limit).offset(offset).order_by(order)

	rows=[]
	for row in queryResult.limit(limit).offset(offset):
		# print "row.report_pc_count:", row.report_pc_count
		rows.append(\
			{"MD5_KEY":row.md5_key, \
			 "FILE_NAME": row.file_name, \
			 "RESULT_NUMBER":row.result_number, \
			 "VIRUS_NAME":row.virus_name,\
			 "SIGN_CREDIT":str(row.sign_credit), \
			 "REPORT_PC_COUNT":str(row.report_pc_count), \
			 "SAVED_SIZE":str(row.saved_size), \
			 "FILE_TAG":row.file_tag, \
			 "CTIME":str(row.ctime)\
		})

	total=queryResult.count()
	retval={'total':total, 'rows':rows}
	return json.dumps(retval, default=json_util.default)




def allowed_file(filename):
	ALLOWED_EXTENSIONS = set(['zip'])
	return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS


def postprocessor(value):
	try:
		# print "key:",key
		return int(value)
	except (ValueError, TypeError):

		try:
			if (value.lower()=="true") or (value.lower()=="false"):
				value=bool(value)
			return value
		except:
			return value


@app.route("/analysis/")
def mainpage():
	return render_template('analysis.html')

@app.route("/query/<query>/")
def startpage(query):
	return render_template('analysis.html', query=query)

@app.route("/md5list/", methods=['POST'])
def md5list():
	query=request.form.getlist('md5list[]')
	return render_template('analysis.html', md5list=";".join(query))

@app.route("/count/", methods=['POST'])
def count():
	query=request.form.get('query')
	key=query.split("=")[0]
	val=postprocessor(query.split("=")[1])
	data=col_behavior.find({key:val}).count()
	return json.dumps(data, default=json_util.default)

@app.route("/count/and/", methods=['POST'])
def count_and():
	query=request.form.getlist('query[]')
	queryList=[]
	for keyval in query:
		key=keyval.split("=")[0]
		val=postprocessor(keyval.split("=")[1])
		queryList.append({key:val})
	data=col_behavior.find({"$and":queryList}).count()
	return json.dumps(data, default=json_util.default)

@app.route("/detail_one/", methods=['POST'])
def detail_one():
	query=request.form.get('query')
	# print request.form
	key=query.split("=")[0]
	val=postprocessor(query.split("=")[1])
	data=col_behavior.find_one({key:val})
	return json.dumps(data, default=json_util.default)	

@app.route("/detail_one/and/", methods=['POST'])
def detail_one_and():
	query=request.form.getlist('query[]')
	queryList=[]
	for keyval in query:
		key=keyval.split("=")[0]
		val=postprocessor(keyval.split("=")[1])
		queryList.append({key:val})
	data=col_behavior.find_one({"$and":queryList})
	return json.dumps(data, default=json_util.default)

@app.route("/list/", methods=['GET','POST'])
def list():
	if request.method=="POST":
		# print "POST", request.form
		query = request.form.get('query')
		limit = request.form.get('limit')
		offset= request.form.get('offset')
		sort  = request.form.get('sort')
		order = request.form.get('order')
		search= request.form.get('search')
	else:
		# print "GET", request.args
		query = request.args.get('query')
		limit = request.args.get('limit')
		offset= request.args.get('offset')
		sort  = request.args.get('sort')
		order = request.args.get('order')
		search= request.args.get('search')

	try:
		key=query.split("=")[0]
		val=postprocessor(query.split("=")[1])
	except:
		key=query.split("%\3D")[0]
		val=postprocessor(query.split("%\3D")[1])

	# data from mongodb
	md5sumlist=col_behavior.find({key:val}).distinct("md5sum")
	# print "search", search

	return medfileSearch(md5sumlist, search, sort, order, limit, offset)

@app.route("/list/and/", methods=['GET','POST'])
def list_and():
	if request.method=="POST":
		# print "POST", request.form
		query = request.form.getlist('query[]')
		limit = request.form.get('limit')
		offset= request.form.get('offset')
		sort  = request.form.get('sort')
		order = request.form.get('order')
		search= request.form.get('search')
	else:
		# print "GET", request.args
		query = request.args.getlist('query[]')
		limit = request.args.get('limit')
		offset= request.args.get('offset')
		sort  = request.args.get('sort')
		order = request.args.get('order')
		search= request.args.get('search')

	# global cursor
	# print query
	# limit=request.form.get('limit')
	queryList=[]
	for keyval in query:
		key=keyval.split("=")[0]
		val=postprocessor(keyval.split("=")[1])
		queryList.append({key:val})
	md5sumlist=col_behavior.find({"$and":queryList}).distinct("md5sum")
	return medfileSearch(md5sumlist, search, sort, order, limit, offset)

@app.route("/find/common/", methods=['GET','POST'])
def find_intersaction_keyval():
	if request.method=="POST":
		# print "POST", request.form
		query = request.form.getlist('query[]')
		return json.dumps(findCommon(query), default=json_util.default)

@app.route("/remoteupload/zip/", methods=['GET','POST'])
def remove_update_zip():
	try:
		if request.method=="POST":
			file=request.files['file']
			if file and allowed_file(file.filename):
				filename=secure_filename(file.filename)
				filepath=os.path.join(app.config['UPLOAD_FOLDER'], filename)
				file.save(filepath)
				# print "filename: %s" % (filepath)
				import_thread=threading.Thread(target=importer.startImportZip, args=(filepath,))
				import_thread.start()
				return "Upload successful. Started to import zipfile"
		else:
			return "Failed"
	except Exception as e:
		return "Failed: %s" % (e)

@app.route("/")
def dashboard():
	return render_template('dashboard.html')


def getDaterange(input_daterange):
	# print ("input_daterange: %s" % input_daterange)
	strStartDate, strEndDate = input_daterange.split(" - ")
	intCompensationSec=float(32400)
	# print ("strStartDate: %s, strEndDate:%s" % (strStartDate,strEndDate))
	startDate=datetime.fromtimestamp(float(dateParser(strStartDate).strftime('%s'))-intCompensationSec)
	endDate  =datetime.fromtimestamp(float(dateParser(strEndDate  ).strftime('%s'))-intCompensationSec)
	# print ("startDate:%s, endDate: %s" %(startDate, endDate))
	return startDate, endDate


def getTotalPerDay(daterange):
	startDate, endDate = getDaterange(daterange)
	records=col_enginediff.distinct('Date',{'Date':{'$gte':startDate, '$lte':endDate}})
	# sort is not available after distinct.

	# print "before Sort:", records
	records.sort()
	# print "after  Sort:", records

	dateList=set()
	for r in records:
		dateList.add(r)

	# print "after Uniq :", dateList
	# dateList=list(dateList)

	chartCount=[]
	for date in dateList:
		cnt=col_enginediff.distinct('File.MD5', {'Date':date})
		size=len(cnt)
		chartNsec=time.mktime(date.timetuple())*1000
		chartCount.append([chartNsec, size])

	return chartCount

def sortList(seq, idfun=None): 
   # order preserving
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       # in old Python versions:
       # if seen.has_key(marker)
       # but in new ones:
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result

def getArrayPerDay(query, daterange):
	startDate, endDate = getDaterange(daterange)
	qr={'$and':
			[ 
				query,
				{'Date':
					{'$gte':startDate, '$lte':endDate}
				}
			]
		}
	records=col_enginediff.find(qr).sort('Date',1)

	dateList=[]
	for r in records:
		dateList.append(r['Date'])
	dateList=sortList(dateList)

	chartCount=[]
	for date in dateList:
		cnt=col_enginediff.distinct('File.MD5', {'$and':[query, {'Date':date}]})
		size=len(cnt)
		chartNsec=time.mktime(date.timetuple())*1000
		chartCount.append([chartNsec, size])

	return chartCount


def getTotalMaliciousCountArrayPerDay(query, daterange=None):
	startDate, endDate = getDaterange(daterange)
	records=col_enginediff.find(
		{'$and':[
			query,
			{'Date':{'$gte':startDate, '$lte':endDate}}
		]}
	).sort('Date',1)

	dateList=[]
	for r in records:
		dateList.append(r['Date'])
	dateList=sortList(dateList)
	
	chartCount=[]
	for date in dateList:
		cnt=col_enginediff.distinct('File.MD5', {'$and':[query, {'Date':date}]})
		size=len(cnt)
		chartNsec=time.mktime(date.timetuple())*1000
		chartCount.append([chartNsec, size])

	return chartCount


def getTotalMaliciousCount(daterange):
	startDate, endDate = getDaterange(daterange)
	totalMal=len(
		col_enginediff.distinct(
			'File.MD5',
			{
				'$or':
				[
					{'Results.DICA.Result':'MALICIOUS'},
					{'Results.V3.Result':'MALICIOUS'},
					{'Results.Heimdal.Result':'MALICIOUS'},
					{'Results.VirusTotal.Result':'MALICIOUS'},
					{'Results.MDP_VM.Result':'MALICIOUS'}
				],
				'Date':{'$gte':startDate, '$lte':endDate}
			}
		)
	)
	return totalMal


def getTotalInputCount(daterange):
	totalIn=0
	for countAndTime in getTotalPerDay(daterange):
		cnt=countAndTime[1]
		totalIn+=cnt
	return totalIn


def getDetectionEngineCount(engineName, daterange):
	startDate, endDate = getDaterange(daterange)
	key="Results."+engineName+".Result"
	qr={
		key:'MALICIOUS',
		'Date':{'$gte':startDate, '$lte':endDate}
	}

	# print qr
	engineCount=col_enginediff.distinct('File.MD5',qr)
	return len(engineCount)


def returnDICAVersions(daterange):
	DICA_4_1_2_1 = getArrayPerDay({'$and':[
		{'Results.DICA.Result':'MALICIOUS'},
		{'Results.DICA.Version':'4.1.2.1'}
	]}, daterange)

	DICA_5_0_0_54= getArrayPerDay({'$and':[
		{'Results.DICA.Result':'MALICIOUS'},
		{'Results.DICA.Version':'5.0.0.54'}
	]}, daterange)
	DICA_5_0_1_39 = getArrayPerDay({'$and':[
		{'Results.DICA.Result':'MALICIOUS'},
		{'Results.DICA.Version':'5.0.1.39'}
	]}, daterange)
	DICA_New = getArrayPerDay({'$and':[
		{'Results.DICA.Result':'MALICIOUS'},
		{'Results.DICA.Version':{'$ne':'4.1.2.1'}},
		{'Results.DICA.Version':{'$ne':'5.0.0.54'}},
		{'Results.DICA.Version':{'$ne':'5.0.1.39'}}
	]}, daterange)

	retval={
		'v4_1_2_1':DICA_4_1_2_1,
		'v5_0_0_54':DICA_5_0_0_54,
		'v5_0_1_39':DICA_5_0_1_39,
		'Recent':DICA_New
	}
	return retval


def returnEngineRate(engineName, daterange):
	totalMal=getTotalMaliciousCount(daterange)
	totalEngine=getDetectionEngineCount(engineName, daterange)
	engineVsMalPercent=round(float(totalEngine)/float(totalMal)*100,2)
	# print ("totalMal: %.1f, totalEngine: %.1f, engineVsMalPercent: %.1f" % (totalMal, totalEngine, engineVsMalPercent))
	retval={
		engineName:{
			'percent': engineVsMalPercent,
			'count'  : totalEngine,
			'total'  : totalMal
		}
	}
	return retval


def returnOverall(daterange):
	return {'Malicious': getTotalMaliciousCount(daterange), 'Input': getTotalInputCount(daterange) }


def returnAllRate(daterange):
	retval={}
	# print "returnAllRate: daterange: %s" % daterange
	totalMal=getTotalMaliciousCount(daterange)
	for engineName in ['DICA', 'V3', 'Heimdal', 'VirusTotal', 'MDP_VM']:
		totalEngine = getDetectionEngineCount(engineName, daterange)
		percent=0
		# print "totalEngine: %.1f" % totalEngine

		percent=0
		if totalEngine!=0:

			percent=float(totalEngine)/float(totalMal)*100
			# print "percent: %.1f" % percent


		# array_merge
		retval.update({
			engineName: {
				'percent': percent,
				'count'  : totalEngine,
				'total'  : totalMal
			}
		})
	# print retval
	return retval


def calculateDailyPercent(numerator, denominator):
	retval=[]
	for dt, dv in denominator:
		for nt, nv in numerator:
			if dt==nt:
				nv=float(nv)
				dv=float(dv)
				percent=nv/dv*100
				retval.append([dt, percent])
				break
	return retval


def returnEngineDiff(fetchDate):
	TotalData=getTotalPerDay(fetchDate)
	DICAData=getArrayPerDay(
		{'$and':
			[
				{'Results.DICA.Result': "MALICIOUS"},
				{'Results.DICA.Version': {'$ne':'4.1.2.1' }},
				{'Results.DICA.Version': {'$ne':'5.0.0.54'}},
				{'Results.DICA.Version': {'$ne':'5.0.1.39'}}
			]
		}
	, fetchDate)
	V3Data=getArrayPerDay({'Results.V3.Result':'MALICIOUS'}, fetchDate)
	VirusTotalData=getArrayPerDay({'Results.VirusTotal.Result':'MALICIOUS'}, fetchDate)
	HeimdalData=getArrayPerDay({'Results.Heimdal.Result':'MALICIOUS'}, fetchDate)
	MDP_VMData=getArrayPerDay({'Results.MDP_VM.Result':'MALICIOUS'}, fetchDate)
	TotalMalwareData=getTotalMaliciousCountArrayPerDay(
		{
			'$or':
			[
				{'Results.DICA.Result':'MALICIOUS'},
				{'Results.V3.Result':'MALICIOUS'},
				{'Results.Heimdal.Result':'MALICIOUS'},
				{'Results.VirusTotal.Result':'MALICIOUS'},
				{'Results.MDP_VM.Result':'MALICIOUS'}
			]
		}
	, fetchDate)

	DICAPercent       = calculateDailyPercent(DICAData, TotalMalwareData)
	V3Percent         = calculateDailyPercent(V3Data,   TotalMalwareData)
	VirusTotalPercent = calculateDailyPercent(VirusTotalData, TotalMalwareData)
	HeimdalPercent    = calculateDailyPercent(HeimdalData, TotalMalwareData)
	MDP_VMPercent     = calculateDailyPercent(MDP_VMData, TotalMalwareData)
	
	retval={
		'Total':TotalData,
		'TotalMalicious':TotalMalwareData,
		'DICA':DICAData,
		'DICA_percent':DICAPercent,
		'V3':V3Data,
		'V3_percent':V3Percent,
		'VirusTotal':VirusTotalData,
		'VirusTotal_percent':VirusTotalPercent,
		'Heimdal':HeimdalData,
		'Heimdal_percent':HeimdalPercent,
		'MDP_VM':MDP_VMData,
		'MDP_VM_percent':MDP_VMPercent
	}
	# print retval
	return retval

def isset(variable):
	return variable in locals() or variable in globals()

def returnResultTable(fetchDate=None, fetchEngine=None, daterange=None):
	if fetchDate is not None:
		# print "here?"
		fetchdate=float(fetchDate)/1000
		# print "here!"
		fetchDate=datetime.fromtimestamp(fetchdate)
		# print fetchDate
		t=col_enginediff.aggregate([
			{
				'$match': {
					'$and':[
						{'Date':fetchDate}
					]
				}
			},
			{
				'$group': 
				{
					'_id':'$File.MD5',
					'Date':{'$push':'$Date'},
					'File':{'$push':'$File'},
					'Threat':{'$push':'$Threat'},
					'Results':{'$push':'$Results'},
				}
			},
			{
				'$sort':
				{
					'Date':-1
				}
			},
			{
				'$limit':10000
			}
		])

	else:
		startDate, endDate=getDaterange(daterange)
		query=[
			{'$match': {'$and':[{'Date':{'$gte':startDate, '$lte':endDate}}]}},
			{'$group': {
				'_id':'$File.MD5',
				'Date':{'$push':'$Date'},
				'File':{'$push':'$File'},
				'Threat':{'$push':'$Threat'},
				'Results':{'$push':'$Results'},
				}
			},
			{'$sort':{'Date':-1}},
			{'$limit':10000},
		]
		t=col_enginediff.aggregate(query)

	retval=[]
	if t is not None:
		# print "t: %s" % t
		for d in t:
			# print "============ d: %s" % d
			D=d['Results']
			results={}
			for r in D:
				data=r[0]
				v=0
				m=0
				# print data

				try:
					threat_name=d['Threat'][0]['Threat_Name']
				except KeyError:
					threat_name="None"
				info={
					"Date":d['Date'][0].strftime('%Y-%m-%d'),
					"Name":d['File'][0]['Name'],
					"Type":d['File'][0]['Type'],
					"MD5":d['File'][0]['MD5'],
					"CRC64":d['File'][0]['CRC64'],
					"Size":d['File'][0]['Size'],
					"Severity":d['Threat'][0]['Severity'],
					"Threat_Name":threat_name
				}


				try:
					elementVal=data['MDP_VM']
					elementKey="MDP_VM"
					results.update({elementKey+'_Result':elementVal['Result'], elementKey+'_Reason':elementVal['Reason']})
					m=1
				except KeyError:
					pass

				try:
					elementVal=data['V3']
					elementKey="V3"
					results.update({elementKey+'_Result':elementVal['Result'], elementKey+'_Reason':elementVal['Reason']})
					v=1
				except KeyError:
					pass

				try:
					elementVal=data['Heimdal']
					elementKey="Heimdal"
					results.update({elementKey+'_Result':elementVal['Result'], elementKey+'_Reason':elementVal['Reason']})
				except KeyError:
					pass

				try:
					elementVal=data['DICA']
					if elementVal['Version'] in ['4.1.2.1', '5.0.0.54', '5.0.1.39']:
						# skip above version
						raise KeyError
					elementKey="VirusTotal"
					results.update({elementKey+'_Result':elementVal['Result'], elementKey+'_Reason':elementVal['Reason']})
				except KeyError:
					pass

				results.update(info)

				if m==1 and v==1:
					# print results
					pass
				retval.append(results)

				# print retval
	# print retval
	return retval


@app.route("/fetch/enginerate/<engineName>")
def fetchEngineRate(engineName):
	return Response(json.dumps(returnEngineRate(engineName)), mimetype='application/json')


@app.route("/fetch/DICAVersions/")
def fetchDicaVersions():
	fetchDate   = request.args.get('daterange')
	return Response(json.dumps(returnDICAVersions(fetchDate)), mimetype='application/json')

@app.route("/fetch/Overall/")
def fetchOverAll():
	fetchDate   = request.args.get('daterange')
	return Response(json.dumps(returnOverall(fetchDate)), mimetype='application/json')

@app.route("/fetch/AllRate/")
def fetchAllRate():
	fetchDate   = request.args.get('daterange')
	return Response(json.dumps(returnAllRate(fetchDate)), mimetype='application/json')

@app.route("/fetch/ResultTable/")
def fetchResultTable():
	fetchDate   = request.args.get('date')
	fetchEngine = request.args.get('engine')
	daterange   = request.args.get('daterange')
	return Response(json.dumps(returnResultTable(fetchDate, fetchEngine, daterange)), mimetype='application/json')

@app.route("/fetch/EngineDiff/")
def fetchEngineDiff():
	fetchDate   = request.args.get('daterange')
	# print "+="*40
	# print fetchDate
	return Response(json.dumps(returnEngineDiff(fetchDate)), mimetype='application/json')

def csvToJson(csvString):
	keys=[]
	for key in csvString[0].split(","):
		key=key.strip()
		keys.append(key)

	retval=[]
	for data in csvString[1:]:
		cols={}
		row=data.split(",")
		for key, val in zip(keys, row):
			if key=="":
				pass
			cols[key]=val.strip()
		retval.append(cols)
	return retval

def csvToMongo(csvString):
	data=csvToJson(csvString)
	# data=json.dumps(jsonData)
	ret=[]
	# print "data", data
	for elem in data:
		# PreProcessing Rule 
		# print "elem: %s" % elem
		# print type(elem)
		# print "+="*40

		elem['Size']=int(elem['Size'])
		elem['Date']=dateParser(elem['Date'])
		elem['Severity']=int(elem['Severity'])
		if elem['Threat_Name'].lower()=="none" or elem['Threat_Name']=="":
			elem['Threat_Name']=None

		# Processing From here.
		Date=elem['Date']
		elem.pop('Date')

		File={
			"Name": elem['FileName'],
			"Type": elem['Type'],
			"MD5" : elem['MD5'],
			"CRC64":elem['CRC64'],
			"Size": elem['Size']
		}
		elem.pop('FileName')
		elem.pop('Type')
		elem.pop('MD5')
		elem.pop('CRC64')
		elem.pop('Size')

		Threat={
			"Severity":elem['Severity'],
			"Name": elem['Threat_Name']
		}
		elem.pop('Severity')

		for key, val in elem.items():
			Results=[]
			# result(BENIGN|MALICIOUS|SUSPICIOUS) categorization
			if val=="MALICOUS":
				val="MALICIOUS"
			if val in ['not found', 'Not found', 'None', 'none', 'Clean', 'BENIGN', '']:
				result="BENIGN"
				reason=val
			else:
				result=val
				reason=val

			if key.find("DICA") >= 0:
				Engine="DICA"
				EngineVersion=key.replace("DICA_","")
				Result=result
				Reason=reason
			elif key.find("VM_Threat_Name") >= 0:
				Engine="MDP_VM"
				if val.find("/") >= 0 :
					EngineVersion=0
					if reason!="None":
						Result="MALICIOUS"
					else:
						Result="BENIGN"
				else:
					EngineVersion=0
					Result="BENIGN"
					Reason=0
			elif key.find("AhnLab-V3") >= 0 or key.find("Threat_Name")>=0:
				Engine="V3"
				EngineVersion=key
				if result!="BENIGN":
					Result="MALICIOUS"
				else:
					Result=result
			elif key.find("Heimdal")>=0:
				Engine="Heimdal"
				EngineVersion=key
				Result=result
				Reason=reason
				if reason.find("/") >=0:
					Result=result.split("/")[0]
					Reason=result.split("/")[1]
			elif key.find("VirusTotal") >= 0:
				Engine="VirusTotal"
				if val.find("/") >= 0:
					EngineVersion=reason.split("/")[1]
					if int(reason.split("/")[0])>0:
						Result="MALICIOUS"
					else:
						Result="BENIGN"
				else:
					EngineVersion=0
					Result="BENIGN"
					Reason=0
			else:
				Engine=key
				EngineVersion=key
				Result=result
				Reason=reason
			
			Results.append({
				Engine: {
					"Version":EngineVersion,
					"Result":Result,
					"Reason":Reason
				}
			})
			elem.pop(key)

			retval={
				"Date": Date,
				"File": File,
				"Threat": Threat,
				"Results": Results
			}
			retval['mongoResponse']=col_enginediff.insert(retval)
		ret.append(retval)
	return ret


@app.route("/uploadcsv/", methods=['POST','GET'])
def uploadCSV():
	if request.method=="POST":
		file=request.files['file']
		if file:
			filename=secure_filename(file.filename)
			file.save(os.path.join(app.config['CSV_FOLDER'], filename))

			csvString=open(os.path.join(app.config['CSV_FOLDER'], filename),"r").readlines()
			return render_template('upload.html', retval=csvToMongo(csvString))
	else:
		return render_template('upload.html')

@app.route("/test/<mystr>")
def testpage(mystr):
	# return "my function test %s" % mystr
	return render_template('analysis.html',mystr=mystr)

if __name__ == "__main__":
	app.run("0.0.0.0",debug=True)
