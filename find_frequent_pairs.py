def findFrequentPairs(data,paremeter):
	print 'Using association rules to find frequent pairs'
	hashSingle={}
	hashPair={}
	hashResult={}
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
			hashResult[(p[i],p[o])]=[conf,inte,hashSingle[p[i]],hashSingle[p[o]],hashPair[p]]
	outputResult=''
	for k in hashResult.keys():
		if hashResult[k][0]>=paremeter['confidence'] and abs(hashResult[k][1])>=paremeter['interest'] and k[0][:4]!=k[1][:4]:
			hashResult[k[0]]=[{
				"relatedProduct":k[1],
				"rate":hashResult[k][0],
				"confidence":hashResult[k][0],
				"interest":hashResult[k][1],
				"productSupport":hashResult[k][2],
				"relatedProductSupport":hashResult[k][3],
				"setSupport":hashResult[k][4]}]
			outputResult+=','.join([k[0],k[1]]+[str(v) for v in hashResult[k]]+[str(hashResult[k][3]/float(len(data)))])+'\n'
		del hashResult[k]
	output=open('../frequent_pairs.csv','w')
	output.write(outputResult)
	output.close()
	print 'Frequent Pairs Number:',len(hashResult.keys())
	return hashResult
