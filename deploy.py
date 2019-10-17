#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os                                         
import time                                       
import requests
from termcolor import colored
# Variables got from Rundeck job options

       
                               
#error log                                        
def message():                                 
	return colored(time.strftime("%H:%M:%S %d %b %Y"), 'red')

   #get password from user tomcat server
def authentication(TOMCAT_USER):
	# with open("/usr/local/tomcat/conf/tomcat-users.xml") as f:
	# 	data=f.readlines()
	# 	for line in data:
	# 		if TOMCAT_USER in line:
	# 			auth = line.split(' ')
	# 			for  passwd in auth:
	# 				if "password" in passwd:
	# 					pwd = passwd.split('"')[1]
	# 					break
	auth = (TOMCAT_USER,TOMCAT_USER)
	return auth

	#Chdir to war file                              
def locate(WAR_PATH):                                     
   current_dir =  os.getcwd()                     
   if current_dir != WAR_PATH:                  
        os.chdir(WAR_PATH)                      
	
	
def deploy(TOMCAT_URL,WEBAPP_PATH,WAR_PATH,WAR_INFO,TOMCAT_USER):
	print (message() + " : In Progess.............................\n")
	status_code = False
	name_war = WAR_INFO.split('.')[0]
	version = WAR_INFO.split('.')[1]
	api = 'http://{}/manager/text/deploy?path=/{}&war=file:{}/{}.{}.war&update=true&version={}'
	r = requests.get(api.format(TOMCAT_URL,WEBAPP_PATH,WAR_PATH,name_war,version,version) ,auth = authentication(TOMCAT_USER))
	if r.status_code == 200:
		print( message()+ " :\tOK - Deploy war: \n\t\t\t =>>  Success \n\t\t\t =>> status code: {}\n".format(r.status_code))
		print( message()+ " \tFinalize: \n\t\t\t =>>Deploy " + colored(WAR_INFO,'red') + " Success \n")
		status_code = True
	else:
		print( message()+ " :\tERROR - Deploy war \n\t =>> Not Success \n\t=>> status code: {}\n".format(r.status_code))
		print( message()+ " \tFinalize: \n\t\t\t =>> Deploy " + colored(WAR_INFO,'red') + " Not Success \n")
	return status_code	
	
#Checking the existing of WAR files               
def check_war_file_exist(TOMCAT_URL,WEBAPP_PATH,WAR_INFO,TOMCAT_USER):   
	isexist = 'not_exist'
	api = 'http://{}/manager/text/list'
	ListcurrentApp = requests.get(api.format(TOMCAT_URL), auth = authentication(TOMCAT_USER))                            	
	# name_war = WAR_INFO.split('.')[0]
	version = WAR_INFO.split('.')[1]
	for app in ListcurrentApp.content.strip().split("\n"):
		if (WEBAPP_PATH in app) and ("running" in app):
			print (message() + " : Current application =>> \n\t\tname: " + colored(WEBAPP_PATH,'blue') +" \n\t\tVersion: " +colored(app.split('##')[1] ,'blue') )
			print (message() + " : Application status =>> \n\t\t" + colored(app.split(':')[1] ,'blue') )
			if version not in app:
				print (message() + " : " + colored(WEBAPP_PATH,'blue') +" =>>\t exist different verison!!")
				print (message()+" : " + colored(WEBAPP_PATH,'blue') + " ready to deploy new version! ")
				isexist = 'exist_diff_version'
			else:
				print (message() + " : "+colored(WAR_INFO,'blue') + " already exist at same version! -> Status: running")
				isexist = 'exist_version'
			break
			
		if (WEBAPP_PATH in app) and ("stopped" in app) :
			print (message() + " : Current application =>> \n\t\t" + colored(WEBAPP_PATH,'blue') +" \n\t\tVersion: " +colored(app.split('##')[1] ,'blue') )
			print (message() + " : Application status =>> \n\t\t" + colored(app.split(':')[1] ,'blue') )
			if version not in app:
				print (message()+" : "+WEBAPP_PATH+" ready to deploy new version! ")
				isexist = 'exist_diff_version_stop'
				return isexist
			else:
				print (message() + " : "+WAR_INFO+" already exist at same version! -> Status: stopped")
				isexist = 'exist_version_stop'
			break
	return isexist

	#stop old war file 
def stopoldwarfile(TOMCAT_URL,WEBAPP_PATH,WAR_INFO,TOMCAT_USER):
	new_version=int(WAR_INFO.split('.')[1])
	old_version='{0:03}'.format(new_version-1)
	# http://localhost:8080/manager/text/stop?path=/hoang?version=001
	api = 'http://{}/manager/text/stop?path=/{}&version={}'
	r = requests.get(api.format(TOMCAT_URL,WEBAPP_PATH,old_version), auth = authentication(TOMCAT_USER))
	print (message()+" : "+r.content)

	
def updeployoldwar(TOMCAT_URL,WEBAPP_PATH,WAR_INFO,TOMCAT_USER):
	new_version=int(WAR_INFO.split('.')[1])
	old_version='{0:03}'.format(new_version-1)
	# http://localhost:8080/manager/text/undeploy?path=/examples
	api = 'http://{}/manager/text/undeploy?path=/{}&version={}'
	r = requests.get(api.format(TOMCAT_URL,WEBAPP_PATH,old_version), auth = authentication(TOMCAT_USER))
	print (message()+" : "+r.content)
	
if __name__ == '__main__':                        
	TOMCAT_URL="@option.tomcat_url@"
	WEBAPP_PATH="@option.webapp_path@"
	TOMCAT_USER="@option.tomcat_user@"
	WAR_PATH="@option.war_path@"
	WAR_INFO="@option.war_info@"
	TOMCAT_PWD="@option.tomcat_pwd@"  
	# print(TOMCAT_URL,WEBAPP_PATH,TOMCAT_USER,WAR_PATH,WAR_INFO)
	locate(WAR_PATH) #CHdir to warfile 'not required'
	print (message() + " : "+colored("======Start Process Deploy War======",'green') )
	print (message() + " : "+colored("Process Check War File Exist ...",'green'))
	status = check_war_file_exist(TOMCAT_URL,WEBAPP_PATH,WAR_INFO,TOMCAT_USER)
	if status == 'not_exist':
		print (message() + colored(" : Ok =>> \t \t War File not exist",'green'))
		print (message() + colored(" : Ready to Deploy war \t \t =>> SUCCESS",'blue'))
		deploy(TOMCAT_URL,WEBAPP_PATH,WAR_PATH,WAR_INFO,TOMCAT_USER)
	elif status == 'exist_diff_version' :
		stopoldwarfile(TOMCAT_URL,WEBAPP_PATH,WAR_INFO,TOMCAT_USER)
		deploy(TOMCAT_URL,WEBAPP_PATH,WAR_PATH,WAR_INFO,TOMCAT_USER)
		updeployoldwar(TOMCAT_URL,WEBAPP_PATH,WAR_INFO,TOMCAT_USER)
	elif status == 'exist_version' :
		print (message() + " : STOP Deploy "+WAR_INFO)
	elif status == 'exist_diff_version_stop':
		deploy(TOMCAT_URL,WEBAPP_PATH,WAR_PATH,WAR_INFO,TOMCAT_USER)
		updeployoldwar(TOMCAT_URL,WEBAPP_PATH,WAR_INFO,TOMCAT_USER)
	else:
		print (message() + " : STOP Deploy "+WAR_INFO)