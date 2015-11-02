#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# coding=utf-8

import os, json, sys, fnmatch, shutil
import pymongo
import xmltodict
import zipfile

connection=pymongo.MongoClient("localhost",27017)
MDPMongoDB=connection.MDPDP
col_behavior=MDPMongoDB.behavior_PE

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
				# print "importing %s" % (filename)
				content=content_file.read()

			xmldict=xmltodict.parse(content, postprocessor=postprocessor)
			xmldict.update({'md5sum':md5sum})
			# print md5sum
			jstr = json.dumps(xmldict)
			jsondoc=json.loads(jstr)
			col_behavior.insert(jsondoc)
			success_count=success_count+1

		except Exception as e:
			print "Import Error: (%s/%s) %s Reason: %s" % ( current_count, total_filecount, filename, str(e) )
		current_count=current_count+1

def startImportZip(zipfilepath):
	# print "zipfilepath:", zipfilepath
	zipfilename=os.path.basename(zipfilepath)
	zipfilepath=os.path.dirname(os.path.abspath(zipfilepath))
	target_zipfile=os.path.join(zipfilepath, zipfilename)
	target_dirname=os.path.join(zipfilepath, zipfilename.replace("_PE_report.zip",""))
	print "Target Directory: %s" % target_dirname
	if not os.path.exists(target_dirname):
		print "Creating Directory: %s" % target_dirname
		os.mkdir(target_dirname)

	print "Checking: ", target_zipfile
	if zipfile.is_zipfile(target_zipfile):
		print "Confirmed: ", target_zipfile, " is a zipfile"
		f=open(target_zipfile,'rb')
		z=zipfile.ZipFile(f)
		print "Unzipping %s to %s" % (zipfilename, target_dirname) 
		for name in z.namelist():
			z.extract(name, target_dirname)
		f.close()

	filelist=[]
	for (dirpath, dirnames, filenames) in os.walk(target_dirname):
		filelist.extend(filenames)	
	
	xml_basedir=os.path.abspath(os.path.join(os.path.dirname( __file__ ), "upload", 'xml'))
	if startImportFile(filelist, target_dirname):
		print "Moving files for storge"
		for filename in filelist:
			# print "xml_basedir", xml_basedir
			xml_storedir=os.path.join(xml_basedir, filename[:2], filename[2:4])
			# print "xml_storedir", xml_storedir
			if not os.path.exists(xml_storedir):
				# print "creating directory"
				os.makedirs(xml_storedir)
			orig_file=os.path.join(target_dirname,filename)
			dest_file=os.path.join(xml_storedir,filename)
			# print "origfile", orig_file
			# print "destifle", dest_file
			os.rename(orig_file, dest_file)
		print "Removing unzip directory"
		shutil.rmtree(target_dirname)
	print "Result: Target %s, Total %s, Success %s, Skip %s" % (target_zipfile, success_count, total_filecount, total_filecount-success_count)
	print "Zip Import Finished"


def startImportFile(filelist, path="."):
	print "Import Started..."
	for filename in filelist:
		insertToMongo(path+"/"+filename)
	return True


if __name__ == '__main__':
	# initialize
	# collection.drop()

	xmlPath=sys.argv[1]
	if os.path.isdir(xmlPath):
		print "%s is path" % xmlPath
		# sys.exit(1)

		filelist=[]
		for (dirpath, dirnames, filenames) in os.walk(xmlPath):
			filelist.extend(filenames)
		startImportFile(filelist)

	elif os.path.isfile(xmlPath):
		startImportZip(xmlPath)
	else:
		print "cannot import. unknown type"
		sys.exit(1)
	
	
	print "%s xml files imported successful. Total %s, Skipped %s" % (success_count, total_filecount, total_filecount-success_count)
