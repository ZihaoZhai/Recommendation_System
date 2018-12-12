import psycopg2
import collections

def findBasicRulesProductSet(env):

	def connect(params):
	    conn = None
	    try:
	        print('Connecting to the PostgreSQL database...')
	        conn = psycopg2.connect(**params)
	        print('Connected...\n')
	        cur = conn.cursor()
	        return cur
	    except (Exception, psycopg2.DatabaseError) as error:
	        print(error)

	def hash(display_id):
		if display_id:
			exist=False
			for e in env['hashRule']:
				if display_id[0] in e['case']:
					exist=True
					params=e[env['rule']]
					if params[-1]=='e':
						params[1]=params[1] if params[1]!='e' else len(display_id)
						key=display_id[params[0]:params[1]]
					else:
						key=display_id[0]
					hashMap[key].add(display_id)
					break
			if not exist:
				exception.add(display_id)
	def pick(display_id):
		exist=False
		for e in env['hashRule']:
			if display_id[0] in e['case']:
				exist=True
				params=e[env['rule']]
				if params[-1]=='e':
					key=display_id[params[0]:params[1]]
					if env['prePick'] and e[env['rule']+'PrePick']!=-1:
						result[display_id]=list(hashMap[key])[:e[env['rule']+'PrePick']] # pick product from start or end can make them different
					else:
						result[display_id]=list(hashMap[key])  # pay attention! low copy here!
				elif params[-1]=='n':
					key=display_id[0]
					candidate=set()
					for d in hashMap[key]:
						if display_id[params[0]:params[1]]!=d[params[0]:params[1]]:
							candidate.add(d)
					if env['prePick'] and e[env['rule']+'PrePick']!=-1:
						result[display_id]=list(candidate)[:e[env['rule']+'PrePick']]
					else:
						result[display_id]=list(candidate)
				break
		if not exist:
			result[display_id]=[]
			unMatched.add(display_id)
			

	cur=connect(env['PostgreSqlConnectParameter'])
	cur.execute('select configurable_sku from product')
	print 'Calculating',env['rule']
	row = cur.fetchone()
	hashMap,exception,result,unMatched=collections.defaultdict(set),set(),collections.defaultdict(set),set()
	print 'hashing all product...'
	while row:
		display_id = row[0]
		hash(display_id)
		row = cur.fetchone()
	print len(exception),'exception\n'
	cur.execute('select display_id from display_unit')
	print 'picking related product...'
	row = cur.fetchone()
	while row:
		display_id=row[0]
		pick(display_id)
		row=cur.fetchone()
	print len(unMatched),'unmatched'
	return result