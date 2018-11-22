from datetime import datetime
import time
import json
import os

import data_cleaner

env=json.loads(open('env.json').read())
for k in env:
	if str(env[k]).isdigit():
		env[k]=int(env[k]) if '.' not in str(env[k]) else float(env[k])
files=os.listdir(env['dataFilesPath'])
filePath=env['dataFilesPath']+env['dataFileName']['cleanedInputData']
if env['dataFileName']['cleanedInputData'] in files and (datetime.utcnow()-datetime.fromtimestamp(os.path.getctime(filePath))).total_seconds()<env['updatePeriod']*24*60*60:
	data=json.loads(open(filePath).read())
	data_cleaner.getDataInfor(data)
else:
	filePath=env['dataFilesPath']+env['dataFileName']['soureInputData']
	if env['dataFileName']['cleanedInputData'] in files and (datetime.utcnow()-datetime.fromtimestamp(os.path.getctime(filePath))).total_seconds()>=env['updatePeriod']*24*60*60:
		print 'Please update data.csv manually'
		data=None
	else:
		data=data_cleaner.readCleanData(env)
		userProduct=open(env['dataFilesPath']+env['dataFileName']['cleanedInputData'],'w')
		userProduct.write(json.dumps(data))
		userProduct.close()
if data:
	print 'calculate result'