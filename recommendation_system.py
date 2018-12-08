import json

import data_cleaner
import find_frequent_pairs
import basic_rules

env=json.loads(open('env.json').read())
for k in env:
	if str(env[k]).isdigit():
		env[k]=int(env[k]) if '.' not in str(env[k]) else float(env[k])
if env['algorithmMethod']=='basicRules':
	data=basic_rules.findBasicRulesProductSet(env['basicRulesParameter'])
else:
	data=data_cleaner.readCleanData(env['dataAggregateParameter'])
	print ''
	if env['algorithmMethod']=='associationRule':
		frequentPairs=find_frequent_pairs.findFrequentPairs(data['train'],env['findFrequentPairsParemeter'])
	elif env['algorithmMethod']=='collaborativeFiltering':
		pass
