#!/usr/bin/python

import sys
import os
import time
import smtplib
import shutil

#Set to 1 for debugging information.. else 0
DEBUG = 1

def d_print(arg):
	if DEBUG==1:
		print arg

def mail(serverURL="smtp.example.com",sender='Informer <devnull@example.com>', to=[], subject='', text=''):
	headers = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (sender, ",".join(to), subject)
	message = headers + text
	mailServer = smtplib.SMTP(serverURL)
	#mailServer.set_debuglevel(1)
	ret=mailServer.sendmail(sender, to, message)
	d_print(ret)
	mailServer.quit()

def show_usage(exitval=0):
	print "Usage"
	print sys.argv[0] + " /path/to/source/repo /path/to/destination/repo [option1] [option2] .."
	sys.exit(exitval)

def changes_files(repo):
	installed_debs={}
	# get installed list
	for root, dirs, files in os.walk(repo+"/installed"):
	        for file in files:
	                for line in open(root+"/"+file):
	                        #d_print ( str(len(line)) + line[-5:-1])
	                        if len(line) > 5 and ".deb" == line[-5:-1]:
	                                fields=line.split(" ")
	                                fname=fields[-1]
	                                fnamefields=fname.split("_")
	                                if not installed_debs.has_key(fnamefields[0]):
	                                        installed_debs[fnamefields[0]]=(fnamefields[1],fields[1])
						#installed_debs[fnamefields[0]+"-_md5"]=fields[1]
						#d_print ("Found " + fnamefields[0] + " : " + fnamefields[1])
						#d_print ("md5sum " + fields[1])
	                                else:
	                                        print ("Warning: multiple instance of file " + fnamefields[0] + "; Previous version = " + installed_debs[fnamefields[0]][0])
	return installed_debs


def dict_print(a):
	for key in sorted(a):
		print key," -> ", a[key]

if len(sys.argv) < 3:
        show_usage()


def repocompare (repo1, repo2):
    repo1_installed = changes_files(repo1)
    repo2_installed = changes_files(repo2)
    older_debs=[]
    newer_debs=[]
    noexist_debs=[]
    for key in sorted(repo1_installed):
        if repo2_installed.has_key(key):
            if repo1_installed[key][0] < repo2_installed[key][0]:
                older_debs.append(key)
            elif repo1_installed[key][0] > repo2_installed[key][0]:
                newer_debs.append(key)
        else:
            noexist_debs.append(key)
    return (repo1_installed, repo2_installed, older_debs, newer_debs, noexist_debs)

repo1 = sys.argv[1]
repo2 = sys.argv[2]

# check if valid repo
if not os.path.exists(repo1+"/Release.gpg"):
	print "Are you sure this is a valid repo? Cant find Release.gpg under " + repo1
	sys.exit(2)

if not os.path.exists(repo2+"/Release.gpg"):
	print "Are you sure this is a valid repo? Cant find Release.gpg under " + repo2
	sys.exit(2)

contents, destcontents, older, newer, nonexist = repocompare(repo1,repo2)

print repo1
for package in newer:
    print "newer",package,contents[package][0], "(vs:"+destcontents[package][0]+")"

for package in older:
    print "older",package,contents[package][0], "(vs:"+destcontents[package][0]+")"

for package in nonexist:
    print "only",package,contents[package][0]


