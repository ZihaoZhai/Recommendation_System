import json

import data_cleaner
import find_frequent_pairs

env=json.loads(open('env.json').read())
for k in env:
	if str(env[k]).isdigit():
		env[k]=int(env[k]) if '.' not in str(env[k]) else float(env[k])
# print env
data=data_cleaner.readCleanData(env)
print ''
if data:
	if env['method']=='Association Rule':
		frequentPairs=find_frequent_pairs.findFrequentPairs(data['train'],env['findFrequentPairsParemeter'])
	elif env['method']=='Collaborative Filtering':
		pass
else:
	print "Data is None. You'd better update data.csv."