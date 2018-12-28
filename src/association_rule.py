import collections
import json

def findFrequentPairs(data,paremeter):
	print ('Using association rules to find frequent pairs...')
	data=[data[k] for k in data]
	hashSingle={}
	hashPair={}
	hashResult=collections.defaultdict(dict)
	for d in data:
		for i in xrange(len(d)):
			hashSingle[d[i]]=hashSingle.get(d[i],0)+1
	for k in hashSingle.keys():
		if hashSingle[k]<paremeter['support']:
			del hashSingle[k]
	for d in data:

		for i in xrange(len(d)):
			for j in xrange(i+1,len(d)):
				if d[i] in hashSingle and d[j] in hashSingle:
					hashPair[(d[i],d[j])]=hashPair.get((d[i],d[j]),0)+1
	for p in hashPair:
		for i in xrange(len(p)): # trigger
			o=abs(len(p)-1-i)
			conf=hashPair[p]/float(hashSingle[p[i]]) 
			inte=conf-hashSingle[p[o]]/float(len(data))
			if conf>=paremeter['confidence'] and abs(inte)>=paremeter['interest']:
				hashResult[p[i]][p[o]]=conf
	output=open(paremeter['outPutFile'],'w')
	output.write(json.dumps(hashResult))
	output.close()
	print ('Frequent Pairs Number:',len(hashResult.keys()))
	return hashResult
