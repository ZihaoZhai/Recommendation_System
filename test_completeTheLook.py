from RecommendIDGenerator import connect, RecommendIDGenerator

host = '172.16.3.37'
password = 'evebyeve2020'
dbname = 'datawarehouse_entity_layer'
user = 'datawarehouseapi'
params = {'host' : host, 'password' : password, 'dbname' : dbname, 'user' : user}

gr = RecommendIDGenerator(params)
gr.fetch()
gr.generate()

def test_completeTheLook_1():
	'''Case 1'''
	for key, values in gr.get_completeTheLook().items():
		#print("%s : %s"%(key, values))
		for value in values:
			if (key[0].isdigit()\
			    and (key[:4] != value[:4] or key == value)):
				assert False
	assert True

def test_completeTheLook_2():
	'''Case 2'''
	for key, values in gr.get_completeTheLook().items():
		#print("%s : %s"%(key, values))
		for value in values:
			if key[0] in ['L', 'V', 'D', 'M'] and (key[:5] != value[:5] or key == value):
				assert False
	assert True

def test_completeTheLook_3():
	'''Case 3'''
	for key, values in gr.get_completeTheLook().items():
		#print("%s : %s"%(key, values))
		for value in values:
			if key[0] == 'N' and (key[:5] != value[:5] or key == value):
				assert False
	assert True

def test_completeTheLook_4():
	'''Case 4'''
	for key, values in gr.get_completeTheLook().items():
		if key[0] == 'H':
			print("%s : %s"%(key, values))
		for value in values:
			if key[0] == 'H' and (key[0] != value[0] or key[:6] == value[:6]):
				assert False
	assert True

def test_completeTheLook_5():
	'''Case 5'''
	for key, values in gr.get_completeTheLook().items():
		#print("%s : %s"%(key, values))
		for value in values:
			if key[0] == 'S' and (key[0] != value[0] or key == value):
				assert False
	assert True

def test_completeTheLook_6():
	'''Case 6'''
	for key, values in gr.get_completeTheLook().items():
		#print("%s : %s"%(key, values))
		for value in values:
			if key[0] in ['R', 'K', 'J'] and (key[0] != value[0] or key == value):
				assert False
	assert True


def test_completeTheLook_7():
	'''Case 7'''
	for key, values in gr.get_completeTheLook().items():
		#print("%s : %s"%(key, values))
		for value in values:
			if key[0] in ['E', 'C'] and (key[:4] != value[:4] or key == value):
				assert False
	assert True


print(gr.proportion)
test_completeTheLook_4()
#test_completeTheLook()