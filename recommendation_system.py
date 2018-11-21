import data_cleaner
from random import random
from datetime import datetime

def splitData(data,testSetRate,testSetNum):
	dataSet={}
	testSets=[{} for i in xrange(testSetNum)]
	trainSet={}
	for k in data:
		ti=int(random()*100)/int(testSetRate*100)
		if ti<testSetNum:
			testSets[ti][k]=data[k]
		else:
			trainSet[k]=data[k]
	dataSet['test']=testSets
	dataSet['train']=trainSet
	return dataSet




testSetRate=0.02
testSetNum=5
method='cus'
data=data_cleaner.readCleanData('../data.csv',method)


# dataSet=splitData(data,testSetRate,testSetNum)
# print len(dataSet['train'])


