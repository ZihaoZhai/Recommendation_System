from RecommendIDGenerator import connect, RecommendIDGenerator

host = '172.16.3.37'
password = 'evebyeve2020'
dbname = 'datawarehouse_entity_layer'
user = 'datawarehouseapi'
params = {'host' : host, 'password' : password, 'dbname' : dbname, 'user' : user}

gr = RecommendIDGenerator(params)
gr.fetch()
gr.generate()

def test_alsolike_1():
	'''Case 1 and 2'''
	for key, values in gr.get_youAlsoLike().items():
		#print("%s : %s"%(key, values))
		for value in values:
			if (key[0].isdigit() or key[0] in ['L', 'V', 'D', 'M'])\
			    and (key[-3:] != value[-3:] or key == value):
				assert False
	assert True

def test_alsolike_2():
	'''Case 3'''
	for key, values in gr.get_youAlsoLike().items():
		#print("%s : %s"%(key, values))
		for value in values:
			if key[0] == 'N' and (key[5:7] != value[5:7] or key == value):
				assert False
	assert True

def test_alsolike_3():
	'''Case 4'''
	for key, values in gr.get_youAlsoLike().items():
		#print("%s : %s"%(key, values))
		for value in values:
			if key[0] == 'H' and (key[:6] != value[:6] or key == value):
				assert False
	assert True

def test_alsolike_4():
	'''Case 5'''
	for key, values in gr.get_youAlsoLike().items():
		#if key[0] == 'S':
		#	print("%s : %s"%(key, values))
		for value in values:
			if key[0] == 'S' and (key[:5] == value[:5] or key[-2:] != value[-2:]):
				assert False
	assert True

def test_alsolike_5():
	'''Case 6'''
	for key, values in gr.get_youAlsoLike().items():
		#print("%s : %s"%(key, values))
		for value in values:
			if key[0] in ['R', 'K', 'J'] and (key[0] != value[0] or key == value):
				assert False
	assert True

def test_alsolike_6():
	'''Case 7'''
	for key, values in gr.get_youAlsoLike().items():
		#print("%s : %s"%(key, values))
		for value in values:
			if key[0] in ['E', 'C'] and (key[:4] != value[:4] or key == value):
				assert False
	assert True

#test_alsolike_4()


#test_alsolike()