import json

import data_cleaner
import association_rule
import basic_rules

env=json.loads(open('env.json').read())
for k in env:
	if str(env[k]).isdigit():
		env[k]=int(env[k]) if '.' not in str(env[k]) else float(env[k])
print 'running', env['algorithmMethod']
if env['algorithmMethod']=='BasicRules':
	algorithm='youAlsoLike'
	env['basicRulesParameter']['rule']=algorithm
	data=basic_rules.findBasicRulesProductSet(env['basicRulesParameter'])
	output=open(env['dataAggregateParameter']['dataFilesPath']+algorithm+'.json','w')
	output.write(json.dumps(data))
	output.close()
	algorithm='completeTheLook'
	env['dataAggregateParameter']['rule']=algorithm
	data=basic_rules.findBasicRulesProductSet(env['basicRulesParameter'])
	output=open(env['dataAggregateParameter']['dataFilesPath']+algorithm+'.json','w')
	output.write(json.dumps(data))
	output.close()
else:
	data=data_cleaner.readCleanData(env['dataAggregateParameter'])
	print '\n\n'
	if env['algorithmMethod']=='AssociationRule':
		frequentPairs=association_rule.findFrequentPairs(data['train'],env['associationRulesParemeter'])
		for r in frequentPairs:
			print r,frequentPairs[r][0]['relatedProduct']
	elif env['algorithmMethod']=='CollaborativeFiltering':
		pass
