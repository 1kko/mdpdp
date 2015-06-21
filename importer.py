#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# coding=utf-8

import os, json, sys, fnmatch
import pymongo
import xmltodict

xmlPath=sys.argv[1]
if not os.path.isdir(xmlPath):
	print "%s is not path" % xmlPath
	sys.exit(1)

connection=pymongo.MongoClient("localhost",27017)
db=connection.MDP
collection=db.behavior
success_count=0
total_filecount=0
current_count=0


def postprocessor(path, key, value):
	try:
		# print "key:",key
		return key, long(value)
	except (ValueError, TypeError):

		try:
			if (value.lower()=="true") or (value.lower()=="false"):
				value=bool(value)
			return key, value
		except:
			return key, value

def insertToMongo(filename):
	global count, xmlPath, success_count, total_filecount, current_count
	md5sum, ext = os.path.splitext(filename)
	total_filecount=len(fnmatch.filter(os.listdir(xmlPath), '*.xml'))

	if ext == ".xml":
		try:
			content=""
			with open(xmlPath+filename,'r') as content_file:
				content=content_file.read()

			xmldict=xmltodict.parse(content, postprocessor=postprocessor)
			xmldict.update({'md5sum':md5sum})
			jstr = json.dumps(xmldict)
			jsondoc=json.loads(jstr)
			collection.insert(jsondoc)
			success_count=success_count+1
		except Exception as e:
			print "(%s/%s) Error: %s Reason: %s" % ( current_count, total_filecount, filename, str(e) )
		current_count=current_count+1



# initialize
# collection.drop()

filelist=[]
for (dirpath, dirnames, filenames) in os.walk(xmlPath):
	filelist.extend(filenames)

for filename in filelist:
	insertToMongo(filename)
	# print filename
	# break

print "%s xml files imported successful. Total %s, Skipped %s" % (success_count, total_filecount, total_filecount-success_count)
