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
		recommendProduct=collections.defaultdict(list)
		key=data.keys()
		start=datetime.now()
		print ( 'Running user-base approach...')
		print ( 'total user:',len(key))
		print ( 'finding similar user and predicting...')
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
						candidateProduct[k1]=candidateProduct[k1]|(s2-s1)
					if k2[0]=='C':
						similarUser[k2][k1]=simi
						candidateProduct[k2]=candidateProduct[k2]|(s1-s2)
			if len(similarUser[k1].keys())>0 and k1[0]=='C':
				total=sum([similarUser[k1][u]**2 for u in similarUser[k1]])
				for pro in candidateProduct[k1]:
					simi=0
					for u in productUserMapping[pro]:
						simi+=similarUser[k1].get(u,0)**2
					simi=simi/float(total)
					if simi>=env['recommendProductThreshold']:
						bisect.insort(recommendProduct[k1],(simi,pro))
				del similarUser[k1]
				if k1 in candidateProduct:
					del candidateProduct[k1]
			count+=1
			if count%1000==0:
				print ( int(count/float(len(key))*100),'%','finished',datetime.now()-start)
		return recommendProduct

	def itemBase(data):
		key=data.keys()
		count=0
		start=datetime.now()
		print ( 'Running items-base approach...' )
		print ( 'total product:',len(key))
		print ( 'finding similar product...')
		relatedData=collections.defaultdict(dict)
		for i in xrange(len(key)):
			for j in xrange(i+1,len(key)):
				k1,k2=key[i],key[j]
				s1,s2=set(data[k1]),set(data[k2])
				simi=jaccardSimilarity(s1,s2)
				if simi>env['itemSimilarityThreshold']:
					relatedData[k1][k2]=simi
					relatedData[k2][k1]=simi
			count+=1
			if count%500==0:
				print ( int(count/float(len(key))*100),'%','finished',datetime.now()-start)
		return relatedData


	productUserMapping=reverseMapping(data)
	if env["method"]=='UserBase':
		result=userBase(data)
		output=open('../Data/recommendProduct_userBase.json','w')
		output.write(json.dumps(result))
		output.close()
	elif env["method"]=='ItemBase':
		result=itemBase(productUserMapping)
		print ( result )
		output=open('../Data/recommendProduct_itemBase.json','w')
		output.write(json.dumps(result))
		output.close()
	return result