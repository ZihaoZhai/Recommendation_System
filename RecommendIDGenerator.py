from collections import defaultdict
import psycopg2
import sys
import json

def connect(params):
    """ 
    Connect to the PostgreSQL database server
    args:
        params : dictionary for connection setting.
    
    return:
        cursor : cursor object for sql manipulation.
    
    """
    #import psycopg2
    conn = None
    try:
        # read connection parameters
        #params = config()
 
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        print('Connected...')
        # create a cursor
        cur = conn.cursor()
        
        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
 
        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
       
        # close the communication with the PostgreSQL
        #cur.close()
        return cur
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def algorithm_case_judge(dis_id):
    
    if dis_id is None or len(dis_id) == 0:
        return -1
    
    n = len(dis_id)
    if dis_id[0].isdigit() and n >= 4:
        return 1
    if dis_id[0] in ['L', 'V', 'D', 'M'] and n >= 5:
        return 2
    if dis_id[0] == 'N' and n >= 7:
        return 3
    if dis_id[0] == 'H' and n >= 6:
        return 4
    if dis_id[0] == 'S' and n >= 5:
        return 5
    if dis_id[0] in ['R', 'K', 'J'] and n > 1:
        return 6
    if dis_id[0] in ['E', 'C'] and n >= 5:
        return 7
    
    return -1

class RecommendIDGenerator:
    '''
        class to generate display-id dictionary based on algorithm logic.
        
        Usage example:
            host = '172.16.3.37'
            password = 'xxxxxxxx'
            dbname = 'datawarehouse_entity_layer'
            user = 'datawarehouseapi'
            params = {'host' : host, 'password' : password, 'dbname' : dbname, 'user' : user}
            
            gr = RecommendIDGenerator(params)
            gr.fetch(sql = 'select configurable_sku from product')
            gr.generate(sql = 'select display_id from list_unit')
            
            CompleteTheLook = gr.get_completeTheLook()
            YouAlsoLike = gr.get_youAlsoLike()
            
    '''
    #from collections import defaultdict
    def __init__(self, params):
        self.cur = connect(params)
        self._completeTheLookSet = defaultdict(set)
        self._youAlsoLikeSet = defaultdict(set)
        self.completeTheLook = defaultdict(list)
        self.youAlsoLike = defaultdict(list)
        self.unusedID = set()
        self.init_proportion()
        #self.proportion = None

    def init_proportion(self):
        with open('env.json') as json_file:
            json_data = json.load(json_file)
            self.proportion = json_data['basicAlgorithmParams']['proportion']
    
    def get_completeTheLook(self):
        '''Used to return complete-the-look recommendation dictionary'''
        return dict(self.completeTheLook)
    
    def get_youAlsoLike(self):
        '''Used to return youAlsoLike recommendation dictionary'''
        return dict(self.youAlsoLike)
    
    def get_unusedID(self):
        '''Used to return unusedID'''
        return list(self.unusedID)
    
    def _get_youAlsoLike_match_key(self, algorithm_case, display_id):
        '''
            generate and return match_key from display_id for youAlsoLike
        '''
        matchKey = ''
        if algorithm_case in [1, 2]:
            matchKey = display_id[-3:]
        elif algorithm_case == 3:
            matchKey = display_id[5:7]
        elif algorithm_case == 4:
            matchKey = display_id[:6]
        elif algorithm_case == 5:
            matchKey = display_id[-2:]
        elif algorithm_case == 6:
            matchKey = display_id[0]
        else:
            matchKey = display_id[:4]
        
        return matchKey
    
    def _get_completeTheLook_match_key(self, algorithm_case, display_id):
        '''
            generate and return match_key from display_id for completeTheLook_match
        '''
        
        matchKey = ''
        if algorithm_case  == 1:
            matchKey = display_id[:4]
        elif algorithm_case in [2, 3]:
            matchKey = display_id[:5]
        elif algorithm_case in [4, 5, 6]:
            matchKey = display_id[0]
        else:
            matchKey = display_id[:4]
        
        return matchKey
        
    
    def fetch(self, sql = 'select configurable_sku from product'):
        '''Run this function first to fetch recommendation list.'''
        self.cur.execute(sql)
        row = self.cur.fetchone()
        while row is not None:
            display_id = row[0]
            algorithm_case = algorithm_case_judge(display_id)
            n = len(display_id)
            
            # Case 1 : SKU start with number:
            if algorithm_case == 1:
                self._completeTheLookSet[display_id[:4]].add(display_id)
                self._youAlsoLikeSet[display_id[-3:]].add(display_id)
            
            # Case 2 : SKU starts with L, V, D, M:
            elif algorithm_case == 2:
                self._completeTheLookSet[display_id[:5]].add(display_id)
                self._youAlsoLikeSet[display_id[-3:]].add(display_id)
                
            #Case 3:
            elif algorithm_case == 3:
                if n == 8 or n == 9:
                    self._completeTheLookSet[display_id[:5]].add(display_id)
                self._youAlsoLikeSet[display_id[5:7]].add(display_id)
            
            #Case 4:
            elif algorithm_case == 4:
                self._completeTheLookSet['H'].add(display_id)
                self._youAlsoLikeSet[display_id[:6]].add(display_id)
            
            #Case 5:
            elif algorithm_case == 5:
                self._completeTheLookSet['S'].add(display_id)
                self._youAlsoLikeSet[display_id[-2:]].add(display_id)
            
            #Case 6:
            elif algorithm_case == 6:
                self._completeTheLookSet[display_id[0]].add(display_id)
                self._youAlsoLikeSet[display_id[0]].add(display_id)
            
            #Case 7:
            elif algorithm_case == 7:
                self._completeTheLookSet[display_id[:4]].add(display_id)
                self._youAlsoLikeSet[display_id[:4]].add(display_id)
            
            #Not satisfy any Case:
            else:
                #self.unusedID.add(display_id)
                pass
                
            row = self.cur.fetchone()
        
    def generate(self, sql = 'select display_id from display_unit'):
        '''Run this function to generate CompleteTheLook and YouAlsoLike list after fetch'''
        self.cur.execute(sql)
        row = self.cur.fetchone()
        while row is not None:
            display_id = row[0]
            algorithm_case = algorithm_case_judge(display_id)
            self._addCompleteTheLook(algorithm_case, display_id)
            self._addYouAlsoLike(algorithm_case, display_id)
            row = self.cur.fetchone()
            if algorithm_case == -1:
                self.unusedID.add(display_id)
    
    def _addCompleteTheLook(self, algorithm_case, display_id):
        if algorithm_case == -1:
            return
        
        matchKey = self._get_completeTheLook_match_key(algorithm_case, display_id)
        
        # First three algorithm cases require to return all matching items.
        # Last four algorithm cases only require 4:
        res = [idx for idx in self._completeTheLookSet[matchKey] \
                   if idx != display_id and \
                      idx[0] == display_id[0]]
        n_res = [idx for idx in res if idx[:6] != display_id[:6]]
        if self.proportion == 'predefined':
            if algorithm_case <= 3:
                self.completeTheLook[display_id] = res
            elif algorithm_case == 4:
                # special case for fourth algorithm
                self.completeTheLook[display_id] = n_res[:4]
            else :
                self.completeTheLook[display_id] = res[:4]
        else:
            if algorithm_case == 4:
                self.completeTheLook[display_id] = n_res
            else:
                self.completeTheLook[display_id] = res

    
    def _addYouAlsoLike(self, algorithm_case, display_id):
        if algorithm_case == -1:
            return
        
        matchKey = self._get_youAlsoLike_match_key(algorithm_case, display_id)
        
        # First five algorithm cases require to return all matching items.
        # Last two algorithm cases only require 4:
        res = [idx for idx in self._youAlsoLikeSet[matchKey] \
                   if idx != display_id and\
                      idx[0] == display_id[0]]
        n_res = [idx for idx in res if idx[:5] != display_id[:5]]

        if self.proportion == 'predefined':
            if algorithm_case < 5:
                self.youAlsoLike[display_id] = res[:6]
            elif algorithm_case == 5:
                # special case for fifth algorithm
                self.youAlsoLike[display_id] = n_res[:6]
            else :
                self.youAlsoLike[display_id] = res[:4]
        else:
            if algorithm_case == 5:
                self.youAlsoLike[display_id] = n_res
            else:
                self.youAlsoLike[display_id] = res



def main():
    host = '172.16.3.37'
    password = 'evebyeve2020'
    dbname = 'datawarehouse_entity_layer'
    user = 'datawarehouseapi'
    params = {'host' : host, 'password' : password, 'dbname' : dbname, 'user' : user}

    if len(sys.argv) <= 2:
        sys.stderr.write("ERROR > Usage : python RecommendIDGenerator.py <Path-you-also-like> <Path-complete-the-look>\n")
        sys.exit(-1)

    path_youAlsoLike = sys.argv[1]
    path_completeTheLook = sys.argv[2]

    gr = RecommendIDGenerator(params)
    gr.fetch()
    gr.generate()

    youAlsoLike = gr.get_youAlsoLike()
    completeTheLook = gr.get_completeTheLook()

    #Write result to file:
    with open(path_completeTheLook, 'w') as f:
        for key in completeTheLook.keys():
            if len(completeTheLook[key]) == 0:
                continue
            f.write("{%s : %s}\n"%(key, completeTheLook[key]))


    with open(path_youAlsoLike, 'w') as f:
        for key in youAlsoLike.keys():
            if len(youAlsoLike[key]) == 0:
                continue
            f.write("{%s : %s}\n"%(key, youAlsoLike[key]))



if __name__ == '__main__':
    main()



