#!/usr/local/bin/python3
# Download images and movies from the Theta S
# 2015-11-07
import sys, json, requests, os, time

thetaURL = "http://192.168.1.1:80"
commandsExecuteURL = thetaURL + "/osc/commands/execute"
commandsStatusURL = thetaURL + "/osc/commands/status"

def sessionStart():
	sessionStart = {'name':'camera.startSession','parameters':{}}
	r = requests.post(commandsExecuteURL, json=sessionStart)
	response = r.json()
	results = response['results']
	sessionId = results['sessionId']
	return sessionId

def closeSession(sessionId):
	closeSession = {'name':'camera.closeSession','parameters':{'sessionId':sessionId}}
	r = requests.post(commandsExecuteURL,json=closeSession)

def takePicture (sessionId):
	inputParm = {'name':'camera.takePicture','parameters':{'sessionId':sessionId}}
	r = requests.post(commandsExecuteURL, json=inputParm)
	response = r.json()
	id = response['id']
	return id

def waitForPictureDone (id):
	inputParm = {'id':id}
	state = "inProgress"
	while state == "inProgress":
		r = requests.post(commandsStatusURL, json=inputParm)
		response = r.json()
		state = response['state']
		print (state)
	results = response['results']
	fileUri = results['fileUri']
	return fileUri

def getImageOrVideo (fileUri):
	splitExt = os.path.splitext(fileUri)
	if splitExt[1] == ".MP4":
		command = 'camera._getVideo'
	else:
		command = 'camera.getImage'
	inputParm = {'name':command,'parameters':{'fileUri':fileUri}}
	r = requests.post(commandsExecuteURL,json=inputParm)
	return r.content

def storeImage (fileUri,dateTimeZone=""):
	splitUri = fileUri.split('/')
	amount = len(splitUri)
	filename = splitUri[amount-1]
	print (filename + " ... ",end="")
	if os.path.exists(filename) == False:
		content = getImageOrVideo (fileUri)
		f = open(filename,'wb')
		f.write(content)
		f.close()
		print ("saved")
		if dateTimeZone != "":
			creationTime = convertDateTimeZone(dateTimeZone)
			creationTime4Utime = time.mktime(creationTime)
			os.utime (filename, (creationTime4Utime,creationTime4Utime))
	else:
		print ("exists")

def listOfImages (entryCount=99999):
	inputParm = {"name":"camera.listImages","parameters":{"entryCount":entryCount,"includeThumb":False}}
	r = requests.post(commandsExecuteURL,json=inputParm)
	response = r.json()
	results = response["results"]
	entries = results["entries"]
	return entries

def listAll (entryCount=99999):
	inputParm = {"name":"camera._listAll","parameters":{"entryCount":entryCount}}
	r = requests.post(commandsExecuteURL,json=inputParm)
	response = r.json()
	results = response["results"]
	entries = results["entries"]
	return entries

def convertDateTimeZone (dateTimeZone):
	convertedTime = time.strptime(dateTimeZone[0:19], "%Y:%m:%d %H:%M:%S")
	return convertedTime

entries = listAll()

for entry in entries:
	storeImage (entry["uri"],entry["dateTimeZone"])
