import json

import data_cleaner
import association_rule
import basic_rules
import collaborative_filtering

env=json.loads(open('env.json').read())
for k in env:
	if str(env[k]).isdigit():
		env[k]=int(env[k]) if '.' not in str(env[k]) else float(env[k])
print 'running', env['algorithmMethod']
if env['algorithmMethod']=='BasicRules':
	data=basic_rules.findBasicRulesProductSet(env['basicRulesParameter'],env['PostgreSqlConnectParameter'])
	output=open(env['dataAggregateParameter']['dataFilesPath']+env['basicRulesParameter']['rule']+'.json','w')
	output.write(json.dumps(data))
	output.close()
else:
	data=data_cleaner.readCleanData(env['dataAggregateParameter'])
	print '\n'
	if env['algorithmMethod']=='AssociationRule':
		frequentPairs=association_rule.findFrequentPairs(data['train'],env['associationRulesParemeter'])
	elif env['algorithmMethod']=='CollaborativeFiltering':
		recommendProduct=collaborative_filtering.collaborativeFiltering(data['train'],env['collaborativeFilteringParameter'])
		
