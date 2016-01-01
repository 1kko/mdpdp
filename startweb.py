#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# coding=utf-8

from flask import Flask, render_template, request, url_for, Response, redirect, send_from_directory, abort, jsonify
import flask.ext.login as flask_login
import os
from werkzeug import secure_filename
from bson import json_util
import pymongo, json
from peewee import *
from playhouse.pool import MySQLDatabase
import threading
import sys
from dateutil.parser import parse as dateParser
from datetime import datetime
import time
import pytz

# sys.path.insert(0, '/home/ikko/repo/mdpdp/')
import importer
from reversediff import findCommon

connection=pymongo.MongoClient("localhost",27017,tz_aware=True)
MDPMongoDB=connection.MDPDP
col_behavior=MDPMongoDB.behavior_PE
col_enginediff=MDPMongoDB.enginediff_PE
login_manager=flask_login.LoginManager()

count=0

database = MySQLDatabase('MEDDB', **{'password': 'qwe123', 'user': 'asduser03'})
users={'foo@bar.tld':{'pw':'secret'}}

app=Flask(__name__)


# print "my path:", 
# app.config['MDPDP_BASEDIR']='/home/ikko/repo/mdpdp'
MDPDP_BASEDIR=os.path.dirname(os.path.realpath(__file__))
# print "my path:",MDPDP_BASEDIR
app.config['ZIP_UPLOAD_DIR']=os.path.join(MDPDP_BASEDIR,'upload/zip/')
app.config['CSV_UPLOAD_DIR']=os.path.join(MDPDP_BASEDIR,'upload/csv/')

application=app
login_manager.init_app(app)

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

class User(flask_login.UserMixin):
	pass


@login_manager.user_loader
def user_loader(email):
	if email not in users:
		return

	user = User()
	user.id = email
	return user


@login_manager.request_loader
def request_loader(request):
	email = request.form.get('email')
	if email not in users:
		return

	user = User()
	user.id = email

	# DO NOT ever store passwords in plaintext and always compare password
	# hashes using constant-time comparison!
	user.is_authenticated = request.form['pw'] == users[email]['pw']

	return user

def medfileSearch(md5sumlist, search, sort, order, limit, offset):

	database.get_conn().ping(True)
	# print "md5sumlist:", ', '.join(md5sumlist)[0:67], "...", ', '.join(md5sumlist)[-68:]
	# print "md5sumlist count:", len(md5sumlist)
	# print "search:", search
	# print "sort:", sort
	# print "order:", order
	# print "limit:", limit
	# print "offset:", offset

	if len(md5sumlist) == 0 :
		retval={'total':0, 'rows':[]}

	else:

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
	import HTMLParser
	try:
		return int(value)
	except (ValueError, TypeError):
		# print "not num: escaped value", value
		if (value.lower()=="true"):
			return True
		elif (value.lower()=="false"):
			return False

		return HTMLParser.HTMLParser().unescape(value)



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


def returnResultTable(fetchDate=None, fetchEngine=None, daterange=None):
	if fetchDate is not None:
		# print "here?"
		fetchdate=float(fetchDate)/1000
		# print "here!"
		fetchDate=datetime.fromtimestamp(fetchdate)
		# print fetchDate
		query=[
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
		]
		documents=col_enginediff.aggregate(query, allowDiskUse=True)

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
		documents=col_enginediff.aggregate(query, allowDiskUse=True)

	retval=[]
	if documents is not None:
		# print "t: %s" % t
		for document in documents:
			# print "============ document: %s" % document
			# results={}

			threat_name="None"
			if document['Threat'][0].has_key('Name'):
				threat_name=document['Threat'][0]['Name']

			crc64="None"
			if document['File'][0].has_key('CRC64'):
				crc64=document['File'][0]['CRC64']

			info={
				"Date":document['Date'][0].strftime('%Y-%m-%d'),
				"Name":document['File'][0]['Name'],
				"Type":document['File'][0]['Type'],
				"MD5":document['File'][0]['MD5'],
				"CRC64":crc64,
				"Size":document['File'][0]['Size'],
				"Severity":document['Threat'][0]['Severity'],
				"Threat_Name":threat_name
			}

			results={}
			for Results in document['Results']:
				if Results.has_key('MDP_VM'):
					elementVal=Results['MDP_VM']
					elementKey="MDP_VM"
					results.update({elementKey+'_Result':elementVal['Result'], elementKey+'_Reason':elementVal['Reason']})
					# m=1

				if Results.has_key('V3'):
					elementVal=Results['V3']
					elementKey="V3"
					results.update({elementKey+'_Result':elementVal['Result'], elementKey+'_Reason':elementVal['Reason']})
					# print elementKey, elementVal
					# v=1

				if Results.has_key('Heimdal'):
					elementVal=Results['Heimdal']
					elementKey="Heimdal"
					results.update({elementKey+'_Result':elementVal['Result'], elementKey+'_Reason':elementVal['Reason']})

				if Results.has_key('DICA'):
					elementVal=Results['DICA']
					if elementVal['Version'] in ['4.1.2.1', '5.0.0.54', '5.0.1.39']:
						# skip above version
						raise KeyError
					elementKey="VirusTotal"
					results.update({elementKey+'_Result':elementVal['Result'], elementKey+'_Reason':elementVal['Reason']})
				
				info.update(results)

				# if m==1 and v==1:
				# 	print results
				# 	pass
			# info.update(results)
			retval.append(info)
			# print "appending info: %s" % info
			# print "=-"*40
			# print info


			# info.update(retval)	# print retval
	# print retval
	return retval


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
	Seoul=pytz.timezone('Asia/Seoul')
	data=csvToJson(csvString)
	# print data
	# data=json.dumps(jsonData)
	mongoRetval=[]
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
		if elem.has_key("CRC64") is not True:
			elem['CRC64']=None

		# Processing From here.
		Date=Seoul.localize(elem['Date'])
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
			"Name": elem['Threat_Name'],
			"VM_Severity":elem['Result']
		}
		elem.pop('Severity')
		elem.pop('Result')

		Results={}
		for key, val in elem.items():
			# result(BENIGN|MALICIOUS|SUSPICIOUS) categorization
			if key=='':
				pass
			else:
				if val=="MALICOUS":
					val="MALICIOUS"
				if val in ['not found', 'Not found', 'None', 'none', 'Clean', 'BENIGN', '', None]:
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
						Reason=reason
						if reason!="None":
							Result="MALICIOUS"
						else:
							Result="BENIGN"
							Reason=None
					else:
						EngineVersion=0
						Result="BENIGN"
						Reason=None
				elif key.find("AhnLab-V3") >= 0 or key.find("Threat_Name")>=0:
					Engine="V3"
					EngineVersion="AhnLab-V3"
					Reason=reason
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
						EngineVersion=int(reason.split("/")[1])
						Reason=int(reason.split("/")[0])
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


				# print "Engine: %s" % Engine
				Results.update({
					Engine: {
						"Version":EngineVersion,
						"Result":Result,
						"Reason":Reason
					}
				})
			# print Results
			# elem.pop(key)

		retval={
				"Date": Date,
				"File": File,
				"Threat": Threat,
				"Results": Results
		}
		# ret.append(retval)
		# print "Insert: %s" % retval
		mongoRetval.append(col_enginediff.insert(retval))
	return mongoRetval

def escapeHtml(s, quote=None):
	'''Replace special characters "&", "<" and ">" to HTML-safe sequences.
	If the optional flag quote is true, the quotation mark character (")
is also translated.'''
	# if type(s) == type(str()):
	try:
		s = s.replace("&", "&amp;") # Must be done first!
		s = s.replace("<", "&lt;")
		s = s.replace(">", "&gt;")
		s = s.replace('"', "&quot;")
		s = s.replace("'", "&#39;")
		return s
	except:
		return s


def queryToDict(query):
	try:
		Query=query
		if query.startswith(" "):
			Query=query[1:]

		# if key starts with { it means it's json type.
		if Query.startswith("{"):
			key, val=json.loads(query.replace("'","\"")).items()[0]
		else:
		# otherwise it means it's aaa.bb.cc=ccc type
			idx=Query.find("=")
			key=Query[:idx]
			val=Query[idx+1:]
		
		Val=postprocessor(val)
		retval={key:Val}

		print "retval",retval
		return retval
	except:
		raise


@login_manager.unauthorized_handler
def unauthorized_handler():
	return 'Unauthorized'


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


@app.route("/login", methods=['POST', 'GET'])
def login():
	if request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='pw' id='pw' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form>
			   '''

	email = request.form['email']
	if request.form['pw'] == users[email]['pw']:
		user = User()
		user.id = email
		flask_login.login_user(user)
		return redirect(url_for('protected'))

	return 'Bad login'


@app.route('/protected')
@flask_login.login_required
def protected():
	return 'Logged in as: ' + flask_login.current_user.id


@app.route('/logout')
def logout():
	flask_login.logout_user()
	return 'Logged out'


@app.route("/analysis/")
def mainpage():
	return render_template('analysis.html')


@app.route("/query/<query>/")
def startpage(query):
	return render_template('analysis.html', query=query)


@app.route("/analysis/md5list/", methods=['POST'])
def md5list():
	query=request.form.getlist('md5list[]')
	return render_template('analysis.html', md5list=";".join(query))


@app.route("/count/", methods=['POST'])
def count():
	query=request.form.get('query')
	# print query
	data=col_behavior.find(queryToDict(query)).distinct("md5sum")
	return json.dumps(len(data), default=json_util.default)


@app.route("/count/and/", methods=['POST'])
def count_and():
	query=request.form.getlist('query[]')
	queryList=[]
	print "queries: %s" % query

	for keyval in query:
		queryList.append(queryToDict(keyval))
	data=col_behavior.find({"$and":queryList}).distinct("md5sum")
	return json.dumps(len(data), default=json_util.default)


@app.route("/detail_one/", methods=['POST'])
def detail_one():
	query=request.form.get('query')
	# print request.form
	data=json_util.dumps(col_behavior.find(queryToDict(query)).sort('mdpLog.behavior.behaviorData.@tick',1))

	return json_util.dumps(data)

@app.route("/detail_one/and/", methods=['POST'])
def detail_one_and():
	query=request.form.getlist('query[]')
	queryList=[]
	for keyval in query:
		queryList.append(queryToDict(keyval))

	data=col_behavior.find({"$and":queryList}).sort({'mdpLog.behavior.behaviorData.@tick':1})
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

	# data from mongodb
	md5sumlist=col_behavior.find(queryToDict(query)).distinct("md5sum")
	
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
	print "query", query
	# limit=request.form.get('limit')
	queryList=[]
	try:
		for keyval in query:
			queryList.append(queryToDict(keyval))
			print "queryList", queryList
	# if query list is singlular
	except OperationFailure:
		queryList.append(queryToDict(query))

	md5sumlist=col_behavior.find({"$and":queryList}).distinct("md5sum")
	return medfileSearch(md5sumlist, search, sort, order, limit, offset)


@app.route("/list/or/", methods=['POST','GET'])
def list_or():
	if request.method=="POST":
		print "POST", request.form
		query = request.args.getlist('query[]')
		limit = request.args.get('limit')
		offset= request.args.get('offset')
		sort  = request.args.get('sort')
		order = request.args.get('order')
		search= request.args.get('search')
		print "POST", query, limit, offset, sort, order, search
	else:
		# print "GET", request.args
		query = request.args.getlist('query[]')
		limit = request.args.get('limit')
		offset= request.args.get('offset')
		sort  = request.args.get('sort')
		order = request.args.get('order')
		search= request.args.get('search')

	queryList=[]
	for keyval in query:
		queryList.append(queryToDict(keyval))

	md5sumlist=col_behavior.distinct('md5sum',{"$or":queryList})

	return medfileSearch(md5sumlist, search, sort, order, limit, offset)


@app.route("/find/common/", methods=['GET','POST'])
def find_intersaction_keyval():
	if request.method=="POST":
		print "POST", request.form
		query = request.get_json().get('query')
		print "query", query
		orgCommonData=findCommon(query)
		newCommonData=orgCommonData.copy()

		# filter out unnecessary keys.
		for key in orgCommonData:
			# Key starts with
			if key.startswith('mdpLog.analysisOption') or \
				key.startswith('mdpLog.analysisDevice') or \
				key.startswith('mdpLog.targetSample.file'):
					print "deleting %s: %s" % (key, orgCommonData[key])
					del newCommonData[key]
			# EXACT MATCH
			if key in [
				'mdpLog.@version',
				'mdpLog.behavior.behaviorData.@index',
				'mdpLog.behavior.behaviorData.@severity',
				'mdpLog.behavior.behaviorData.@behavior_idx',
				'mdpLog.behavior.behaviorData.@tick',
				'mdpLog.behavior.behaviorData.@id',
				'mdpLog.behavior.behaviorData.detailMsg',
				'mdpLog.behavior.behaviorData.currentProcess.pid',
				'mdpLog.behavior.behaviorData.currentProcess.parentPid',
				'mdpLog.behavior.behaviorData.currentProcess.fileInfo.blockCount',
				'mdpLog.behavior.behaviorData.currentProcess.fileInfo.ctime',
				'mdpLog.behavior.behaviorData.currentProcess.fileInfo.countryCode',
				'mdpLog.behavior.behaviorData.currentProcess.fileInfo.format.#text',
				'mdpLog.behavior.behaviorData.currentProcess.fileInfo.format.@desc',
				'mdpLog.behavior.behaviorData.currentProcess.fileInfo.reputationMsg',
				'mdpLog.behavior.behaviorData.currentProcess.fileInfo.resultNumber.#text',
				'mdpLog.behavior.behaviorData.currentProcess.fileInfo.resultNumber.@desc',
				'mdpLog.behavior.behaviorData.currentProcess.fileInfo.filename',
				'mdpLog.behavior.behaviorData.currentProcess.fileInfo.path',
				'mdpLog.behavior.behaviorData.MdpFlagDescription.@value_0',
				'mdpLog.behavior.behaviorData.MdpFlagDescription.@value_1',
				'mdpLog.behavior.behaviorData.longMsg',
				'mdpLog.behavior.behaviorData.target.fileInfo.reputationMsg',
			]:
				print "deleting %s: %s" % (key, orgCommonData[key])
				del newCommonData[key]


		print "finished common calculation"
		print "="*80
		print "newCommonData"
		print newCommonData
		retCommonData=[]
		for key in newCommonData:
			for value in newCommonData[key]:
				if value not in [None, '']:
					print 'key', key, 'value', value
					retCommonData.append({'key':key, 'value':escapeHtml(value)})

		return json.dumps(retCommonData, default=json_util.default)


@app.route("/remoteupload/zip/", methods=['GET','POST'])
def remove_updload_zip():
	try:
		if request.method=="POST":
			file=request.files['file']
			if file and allowed_file(file.filename):
				filename=secure_filename(file.filename)
				filepath=os.path.join(app.config['ZIP_UPLOAD_DIR'], filename)
				file.save(filepath)
				print "Zip Import Request:", filepath
				import_thread=threading.Thread(target=importer.startImportZip, args=(filepath,))
				import_thread.start()
				return """{"return":"OK", "filename":"%s", "msg":"Upload successful. Started to import zip"}""" % filename
		else:
			return """{"return":"FAIL", "msg":"Upload failed. Please use POST method"}"""
	except Exception as e:
		return """{"return":"FAIL", "msg":"%s"}""" % str(e)


@app.route("/remoteupload/csv/", methods=['POST'])
def remove_updload_csv():
	# curl --include --form file=@151025_pe_mds6000_FillNone.csv http://192.168.41.1/uploadcsv
	if request.method=="POST":
		file=request.files['file']
		if file:
			filename=secure_filename(file.filename)
			filepath=os.path.join(app.config['CSV_UPLOAD_DIR'], filename)
			file.save(filepath)
			print "Csv Import Request:", filepath
			csvString=open(os.path.join(app.config['CSV_UPLOAD_DIR'], filename),"r").readlines()
			imported_csv_row=len(csvToMongo(csvString))
			print "Result: Target %s, Total %s" % (filename, imported_csv_row)
			print "Csv Import Finishd"
			return """{"return":"OK", "inserted":"%s", "filename":"%s","msg":"Upload Successful."}""" % (imported_csv_row, filename)
	else:
		return """{"return":"FAIL", "msg":"Upload failed. Please use POST method"}"""


@app.route("/download/<md5>", methods=['GET'])
def download(md5, fileType="xml"):
	if request.method=="GET":
		if request.args.get('fileType'):
			fileType = request.args.get('fileType')

		fileBaseDir=os.path.abspath(os.path.join(os.path.dirname( __file__ ), "upload", 'xml' ))
		fileName = md5+"."+fileType
		dirPath = os.path.join(fileBaseDir, md5[:2], md5[2:4])
		filePath = os.path.join(dirPath, fileName)

		print "md5", md5
		print "filePath", filePath
		print "fileType", fileType

		if os.path.isfile(filePath):
			if request.args.get('isCheck') == "true":
				print "return ok!"
				return """{"return":"ok"}"""
			else:
				print "sending file"
				return send_from_directory(dirPath, fileName, mimetype='application/octet-stream')
		else:
			abort(404)


@app.route("/get/json/<md5>", methods=['GET'])
def getData(md5):
	if request.method=="GET":
		data=col_behavior.find({"md5sum":md5},{'mdpLog.behavior.behaviorData':1}).sort({'mdpLog.behavior.behaviorData.@tick':1})
		print "data",data
		return json.dumps(data, default=json_util.default)


@app.route("/xmlview/<md5>", methods=['GET'])
def xmlview(md5, fileType="html"):
	if request.method=="GET":
		return render_template('xmlview.html', md5=md5)
	else:
		abort(404)


@app.route("/")
def dashboard():
	return render_template('dashboard.html')


if __name__ == "__main__":
	app.run("0.0.0.0",debug=True)
