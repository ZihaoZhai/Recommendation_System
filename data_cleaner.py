import collections
from datetime import datetime

def customerResolution(data):
	num=0
	start=datetime.now()
	userNum=-1
	while userNum!=len(data.keys()):
		userNum=len(data.keys())
		keys=data.keys()
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
				print 'customer resolution:',num,datetime.now()-start
		break
	return [data[k] for k in data]

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

def aggregateByCustomer(data_obj_list):
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
	print 'userNum',len(data)
	return [obj['configurable_sku'] for obj in data if len(data['configurable_sku']>1)]

def aggregateByOrder(data_obj_list):
	data=collections.defaultdict(set)
	for obj in data_obj_list:
		order=obj['order_id']
		item=obj['configurable_sku']
		data[order].add(item)
	return [data[k] for k in data if len(data[k])>1]

def readCleanData(filePath,method):
	source_data=open(filePath,'r').read().decode("utf-16").split('\n')
	header=source_data.pop(0).split('\t')
	source_data.pop()
	key_mapping={}
	for i in xrange(len(header)):
		key_mapping[i]=header[i]
	data_obj_list=[]
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
		data_obj_list.append(obj)
	print 'start aggregate data'
	if method=='cus':
		return aggregateByCustomer(data_obj_list)
	if method=='ord':
		return aggregateByOrder(data_obj_list)