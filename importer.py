#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# coding=utf-8

import os, json, sys, fnmatch
import pymongo
import xmltodict
import zipfile

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
	global count, success_count, total_filecount, current_count
	md5sum, ext = os.path.splitext(os.path.basename(filename))
	xmlPath=os.path.dirname(os.path.abspath(filename))
	total_filecount=len(fnmatch.filter(os.listdir(xmlPath), '*.xml'))

	if ext == ".xml":
		try:
			content=""
			with open(filename,'r') as content_file:
				print "importing %s" % (filename)
				content=content_file.read()

			xmldict=xmltodict.parse(content, postprocessor=postprocessor)
			xmldict.update({'md5sum':md5sum})
			print md5sum
			jstr = json.dumps(xmldict)
			jsondoc=json.loads(jstr)
			collection.insert(jsondoc)
			success_count=success_count+1
		except Exception as e:
			print "(%s/%s) Error: %s Reason: %s" % ( current_count, total_filecount, filename, str(e) )
		current_count=current_count+1

def startImportZip(zipfilepath):
	zipfilename=os.path.basename(zipfilepath)
	target_dirname=zipfilename.replace("_PE_report.zip","")
	if not os.path.exists(target_dirname):
		os.mkdir(target_dirname)

	if zipfile.is_zipfile(zipfilepath):
		f=open(zipfilepath,'rb')
		z=zipfile.ZipFile(f)
		print "Unzipping %s" % (zipfilepath)
		for name in z.namelist():
			outpath=os.getcwd()+"/"+target_dirname
			z.extract(name, outpath)
		f.close()

	filelist=[]
	for (dirpath, dirnames, filenames) in os.walk(target_dirname):
		filelist.extend(filenames)	
	return startImportFile(filelist, target_dirname)


def startImportFile(filelist, path="."):
	for filename in filelist:
		print "importing %s" % (path+"/"+filename)
		insertToMongo(os.getcwd()+"/"+path+"/"+filename)
	return "SUCCESS"


if __name__ == '__main__':
	# initialize
	# collection.drop()

	xmlPath=sys.argv[1]
	if not os.path.isdir(xmlPath):
		print "%s is not path" % xmlPath
		sys.exit(1)

	filelist=[]
	for (dirpath, dirnames, filenames) in os.walk(xmlPath):
		filelist.extend(filenames)
	startImportFile(filelist)

		# print filename
		# break

	print "%s xml files imported successful. Total %s, Skipped %s" % (success_count, total_filecount, total_filecount-success_count)
