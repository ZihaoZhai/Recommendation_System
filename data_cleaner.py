import collections
from datetime import datetime
from random import random
import os
import json

def getDataInfor(dataSet):
	print 'tarinning set size:',len(dataSet['train'])
	for i in xrange(len(dataSet['test'])):
		print 'testing set '+str(i+1)+' :',len(dataSet['test'][i])

def aggregateByCustomer(data_obj_list):

	def customerResolution(data):
		num=0
		start=datetime.now()
		userNum=-1
		while userNum!=len(data.keys()):
			userNum=len(data.keys())
			keys=data.keys()
			total=len(keys)
			for c in keys:
				for k in data:
					if c!=k and (data[c]['email']&data[k]['email'] or data[c]['telephone']&data[k]['telephone']):
						data[k]['email']=data[k]['email']|data[c]['email']
						data[k]['telephone']=data[k]['telephone']|data[c]['telephone']
						data[k]['configurable_sku']=data[k]['configurable_sku']|data[c]['configurable_sku']
						del data[c]
						break
				num+=1
				if num%2000==0:
					print 'customer resolution:',str(int(num/float(total)*100))+'%',datetime.now()-start
			break
		return [data[k] for k in data]

	data={}
	incremntalId=0
	for obj in data_obj_list:
		user=obj['customer_id']
		if not user:
			user='empty_'+str(incremntalId)
			incremntalId+=1
		if user not in data:
			data[user]={}
			for k in obj:
				data[user][k]=set([obj[k]]) if obj[k] else set()
		else:
			for k in obj:
				if obj[k]:
					data[user][k].add(obj[k])
	singleUser=[]
	for k in data.keys():
		if not data[k]['telephone'] and not data[k]['email']:
			singleUser.append(data[k])
			del data[k]
	data=singleUser+customerResolution(data)
	return [sorted(list(obj['configurable_sku'])) for obj in data if len(obj['configurable_sku'])>1]

def aggregateByOrder(data_obj_list):
	data=collections.defaultdict(set)
	for obj in data_obj_list:
		order=obj['order_id']
		item=obj['configurable_sku']
		data[order].add(item)
	return [sorted(list(data[k])) for k in data if len(data[k])>1]

def readCleanData(env):

	def phoneNumberCleaner(s):
		data=[]
		for c in s:
			if c.isdigit():
				data.append(c)
		data=''.join(data)
		if 10<=len(data)<=12:
			return data[-10:]
		if len(data)==13:
			return data[-11:]
		return None

		

	source_data=open(env['dataFilesPath']+env['dataFileName']['soureInputData'],'r').read().decode("utf-16").split('\n')
	header=source_data.pop(0).split('\t')
	source_data.pop()
	key_mapping={}
	for i in xrange(len(header)):
		key_mapping[i]=header[i]
	dataSet={
		"train":[],
		"test":[[] for i in xrange(env['testSetNum'])]
	}
	for d in source_data:
		d=d.split('\t')
		obj={}
		if len(d)>len(header):
			d.pop(-3)
		for i in xrange(len(d)):
			obj[key_mapping[i]]=d[i]
		obj['telephone']=phoneNumberCleaner(obj['telephone'])
		obj['email']=None if len(obj['email'])<=10 else obj['email']
		obj['email']=obj['registered_email'] if len(obj['registered_email'])>10 else obj['email']
		singleTestRate=env["testSetRate"]/float(env["testSetNum"])
		ti=int(random()/singleTestRate)
		if ti<env["testSetNum"]:
			dataSet['test'][ti].append(obj)
		else:
			dataSet['train'].append(obj)
	del source_data
	print 'start aggregating testing set'
	print 'total number of testing set:',len(dataSet['test'])
	if env['aggregateMethod']=='cus':
		files=os.listdir(env['dataFilesPath'])
		filePath=env['dataFilesPath']+'userProductMapping.json'
		if 'userProductMapping.json' in files and (datetime.utcnow()-datetime.fromtimestamp(os.path.getctime(filePath))).total_seconds()<env['updatePeriod']*24*60*60:
			dataSet=json.loads(open(filePath).read())
			print 'reading existing data'
			getDataInfor(dataSet)
		else:
			filePath=env['dataFilesPath']+env['dataFileName']['soureInputData']
			if 'userProductMapping.json' in files and (datetime.utcnow()-datetime.fromtimestamp(os.path.getctime(filePath))).total_seconds()>=env['updatePeriod']*24*60*60:
				print 'Please update data.csv manually'
				dataSet=None
			else:	
				for i in xrange(len(dataSet['test'])):
					print 'start aggregating testing set '+str(i+1)
					dataSet['test'][i]=aggregateByCustomer(dataSet['test'][i])
				print 'start aggregating training set'
				dataSet['train']=aggregateByCustomer(dataSet['train'])
				getDataInfor(dataSet)
				userProduct=open(env['dataFilesPath']+'userProductMapping.json','w')
				userProduct.write(json.dumps(dataSet))
				userProduct.close()
	elif env['aggregateMethod']=='ord':
		for i in xrange(len(dataSet['test'])):
			print 'start aggregating testing set '+str(i+1)
			dataSet['test'][i]=aggregateByOrder(dataSet['test'][i])
		print 'start aggregating training set'
		dataSet['train']=aggregateByOrder(dataSet['train'])
		getDataInfor(dataSet)
	return dataSet