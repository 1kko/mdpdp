#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# coding=utf-8

from flask import Flask, render_template, request #, url_for
import pymongo, json, MySQLdb
from bson import json_util

connection=pymongo.MongoClient("localhost",27017)
db=connection.MDP
collection=db.behavior
count=0

rdb=MySQLdb.connect('localhost','asduser03','qwe123','MEDDB')
cursor=rdb.cursor()

app=Flask(__name__)

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


@app.route("/")
def mainpage():
	return render_template('template.html')

@app.route("/count/", methods=['POST'])
def count():
	query=request.form.get('query')
	key=query.split("=")[0]
	val=postprocessor(query.split("=")[1])
	data=collection.find({key:val}).count()
	return json.dumps(data, default=json_util.default)

@app.route("/count/and/", methods=['POST'])
def count_and():
	query=request.form.getlist('query[]')
	queryList=[]
	for keyval in query:
		key=keyval.split("=")[0]
		val=postprocessor(keyval.split("=")[1])
		queryList.append({key:val})
	data=collection.find({"$and":queryList}).count()
	return json.dumps(data, default=json_util.default)

@app.route("/detail_one/", methods=['POST'])
def detail_one():
	query=request.form.get('query')
	key=query.split("=")[0]
	val=postprocessor(query.split("=")[1])
	data=collection.find_one({key:val})
	return json.dumps(data, default=json_util.default)	

@app.route("/detail_one/and/", methods=['POST'])
def detail_one_and():
	query=request.form.getlist('query[]')
	queryList=[]
	for keyval in query:
		key=keyval.split("=")[0]
		val=postprocessor(keyval.split("=")[1])
		queryList.append({key:val})
	data=collection.find_one({"$and":queryList})
	return json.dumps(data, default=json_util.default)

@app.route("/list/", methods=['POST'])
def list():
	query=request.form.get('query')
	# limit=request.form.get('limit')
	key=query.split("=")[0]
	val=postprocessor(query.split("=")[1])
	data=collection.find({key:val}).distinct("md5sum")

	md5sumlist=[]
	for md5sum in data:
		md5sumlist.append(md5sum)

	sql="SELECT MD5_KEY, FILE_NAME, RESULT_NUMBER, VIRUS_NAME, SIGN_CREDIT, REPORT_PC_COUNT, SAVED_SIZE, FILE_TAG, CTIME FROM med_file WHERE MD5_KEY IN (%s) ORDER BY REPORT_PC_COUNT desc, CTIME desc"
	# if (limit=="go_on"):
	# 	sql=sql+" LIMIT 1001,18446744073709551615"
	# else:
	# 	sql=sql+" LIMIT 0,1000"
	# sql=sql+" LIMIT "+limit

	in_p=', '.join(map(lambda x: '%s', md5sumlist))
	sql = sql % in_p
	cursor.execute(sql, md5sumlist)

	retval=[]
	for (MD5_KEY, FILE_NAME, RESULT_NUMBER, VIRUS_NAME, SIGN_CREDIT, REPORT_PC_COUNT, SAVED_SIZE, FILE_TAG, CTIME) in cursor:
		retval.append({"MD5_KEY":MD5_KEY, "FILE_NAME": FILE_NAME, "RESULT_NUMBER":RESULT_NUMBER, "VIRUS_NAME":VIRUS_NAME, "SIGN_CREDIT":SIGN_CREDIT, "REPORT_PC_COUNT":REPORT_PC_COUNT, "SAVED_SIZE":SAVED_SIZE, "FILE_TAG":FILE_TAG, "CTIME":str(CTIME) })
	return json.dumps(retval, default=json_util.default)

@app.route("/list/and/", methods=['POST'])
def list_and():
	query=request.form.getlist('query[]')
	# limit=request.form.get('limit')
	queryList=[]
	for keyval in query:
		key=keyval.split("=")[0]
		val=postprocessor(keyval.split("=")[1])
		queryList.append({key:val})
	data=collection.find({"$and":queryList}).distinct("md5sum")

	md5sumlist=[]
	for md5sum in data:
		md5sumlist.append(md5sum)

	sql="SELECT MD5_KEY, FILE_NAME, RESULT_NUMBER, VIRUS_NAME, SIGN_CREDIT, REPORT_PC_COUNT, SAVED_SIZE, FILE_TAG, CTIME FROM med_file WHERE MD5_KEY IN (%s) ORDER BY REPORT_PC_COUNT desc, CTIME desc"
	# if (limit=="go_on"):
	# 	sql=sql+" LIMIT 1001,18446744073709551615"
	# else:
	# 	sql=sql+" LIMIT 0,1000"
	# sql=sql+" LIMIT "+limit

	in_p=', '.join(map(lambda x: '%s', md5sumlist))
	sql = sql % in_p
	cursor.execute(sql, md5sumlist)

	retval=[]
	for (MD5_KEY, FILE_NAME, RESULT_NUMBER, VIRUS_NAME, SIGN_CREDIT, REPORT_PC_COUNT, SAVED_SIZE, FILE_TAG, CTIME) in cursor:
		retval.append({"MD5_KEY":MD5_KEY, "FILE_NAME": FILE_NAME, "RESULT_NUMBER":RESULT_NUMBER, "VIRUS_NAME":VIRUS_NAME, "SIGN_CREDIT":SIGN_CREDIT, "REPORT_PC_COUNT":REPORT_PC_COUNT, "SAVED_SIZE":SAVED_SIZE, "FILE_TAG":FILE_TAG, "CTIME":str(CTIME) })
	return json.dumps(retval, default=json_util.default)

@app.route("/test/<mystr>")
def testpage(mystr):
	# return "my function test %s" % mystr
	return render_template('template.html',mystr=mystr)

if __name__ == "__main__":
	app.run("127.0.0.1",debug=True)
