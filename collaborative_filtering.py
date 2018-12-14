import collections
import bisect
from datetime import datetime
import json

def collaborativeFiltering(data,env):
	def jaccardSimilarity(s1,s2):
		return len(s1&s2)/float(len(s1|s2))

	def reverseMapping(data):
		newData=collections.defaultdict(list)
		for user in data:
			for pro in data[user]:
				newData[pro].append(user)
		return newData

	def userBase(data):
		similarUser=collections.defaultdict(dict)
		candidateProduct=collections.defaultdict(set)
		productUserMapping=reverseMapping(data)
		recommendProduct=collections.defaultdict(list)
		key=data.keys()
		start=datetime.now()
		print 'total user:',len(key)
		print 'finding similar user and predicting...'
		count=0
		for i in xrange(len(key)):
			for j in xrange(i+1,len(key)):
				k1,k2=key[i],key[j]
				s1,s2=set(data[k1]),set(data[k2])
				if env['similarity']=="Jaccard":
					simi=jaccardSimilarity(s1,s2)
				if simi>=env['userSimilarityThreshold']:
					if k1[0]=='C':
						similarUser[k1][k2]=simi
						candidateProduct[k1]=candidateProduct[k1]|s2
					if k2[0]=='C':
						similarUser[k2][k1]=simi
						candidateProduct[k2]=candidateProduct[k2]|s1
			if len(similarUser[k1].keys())>0:
				total=sum([similarUser[k1][u] for u in similarUser[k1]])
				for pro in candidateProduct[k1]:
					simi=0
					for u in productUserMapping[pro]:
						simi+=similarUser[k1].get(u,0)
					simi=simi/float(total)
					if simi>=env['recommendProductThreshold']:
						bisect.insort(recommendProduct[k1],(simi,pro))
				del similarUser[k1]
				if k1 in candidateProduct:
					del candidateProduct[k1]
			count+=1
			if count%1000==0:
				print int(count/float(len(key))*100),'%','finished',datetime.now()-start
		return recommendProduct

	def itemBase():
		pass

	result=userBase(data)
	output=open('../Data/recommendProduct_userBase.json','w')
	output.write(json.dumps(result))
	output.close()
	print result