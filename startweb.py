#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# coding=utf-8

from flask import Flask, render_template, request, url_for
import os
from werkzeug import secure_filename
import pymongo, json
from bson import json_util
from peewee import *
from playhouse.pool import MySQLDatabase
import importer
import threading

from reversediff import findCommon

connection=pymongo.MongoClient("localhost",27017)
db=connection.MDP
collection=db.behavior
count=0


database = MySQLDatabase('MEDDB', **{'password': 'qwe123', 'user': 'asduser03'})

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

app=Flask(__name__)
UPLOAD_FOLDER = './tmp'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER


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


@app.route("/")
def mainpage():
	return render_template('template.html')

@app.route("/query/<query>/")
def startpage(query):
	return render_template('template.html', query=query)

@app.route("/md5list/", methods=['POST'])
def md5list():
	query=request.form.getlist('md5list[]')
	return render_template('template.html', md5list=";".join(query))

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
	# print request.form
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

@app.route("/list/", methods=['GET','POST'])
def list():
	if request.method=="POST":
		print "POST", request.form
		query = request.form.get('query')
		limit = request.form.get('limit')
		offset= request.form.get('offset')
		sort  = request.form.get('sort')
		order = request.form.get('order')
		search= request.form.get('search')
	else:
		print "GET", request.args
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
	md5sumlist=collection.find({key:val}).distinct("md5sum")
	# print "search", search

	return medfileSearch(md5sumlist, search, sort, order, limit, offset)


@app.route("/list/and/", methods=['GET','POST'])
def list_and():
	if request.method=="POST":
		print "POST", request.form
		query = request.form.getlist('query[]')
		limit = request.form.get('limit')
		offset= request.form.get('offset')
		sort  = request.form.get('sort')
		order = request.form.get('order')
		search= request.form.get('search')
	else:
		print "GET", request.args
		query = request.args.getlist('query[]')
		limit = request.args.get('limit')
		offset= request.args.get('offset')
		sort  = request.args.get('sort')
		order = request.args.get('order')
		search= request.args.get('search')

	# global cursor
	print query
	# limit=request.form.get('limit')
	queryList=[]
	for keyval in query:
		key=keyval.split("=")[0]
		val=postprocessor(keyval.split("=")[1])
		queryList.append({key:val})
	md5sumlist=collection.find({"$and":queryList}).distinct("md5sum")
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
				print "filename: %s" % (filepath)
				import_thread=threading.Thread(target=importer.startImportZip, args=(filepath,))
				import_thread.start()
				return "Upload successful. Started to import zipfile"
		else:
			return "Failed"
	except Exception as e:
		return "Failed: %s" % (e)


@app.route("/test/<mystr>")
def testpage(mystr):
	# return "my function test %s" % mystr
	return render_template('template.html',mystr=mystr)

if __name__ == "__main__":
	app.run("0.0.0.0",debug=True)
