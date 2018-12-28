import psycopg2
from connection import connect
from collections import defaultdict

#Add simple color
def fetch_simpleColors(env):
    #cur = connect(env['PostgreSqlConnectParameter'])
    try:
        conn = connect(env['PostgreSqlConnectParameter'])
        cur = conn.cursor()
        colors = []
        sql = "select color_code from product where category_path <> 'category/materials'"
        cur.execute(sql)
        row = cur.fetchone()
        while row:
            colors.append(row[0])
            row = cur.fetchone()
        return colors
    finally:
        print("close connection...")
        conn.close()
    
    
def simpleColor_dict(env):
    colors = fetch_simpleColors(env)
    simple_dict = {}
    uniqId = 0
    for color in colors:
        if color not in simple_dict.keys() and color != None:
            simple_dict[color] = uniqId
            uniqId += 1
    #print(simple_dict)
    return simple_dict
    
    
def simpleColor_vectors(simpleColors, color_dict):
    '''
        input: 
            color : The color to transform
            color_dict : color-number dictionary
        
        return:
            encoding vector for given color.
    '''

    uniqKeys = list(color_dict.keys())
    encoding_vec = [0 for _ in range(len(uniqKeys))]
    for simpleColor in simpleColors:
        if simpleColor:
            encoding_vec[color_dict[simpleColor]] = 1
    return encoding_vec


def configsku_color_dict(env):
    '''
        input:
            env : parameter environment.
        
        return:
            {configsku1 : [1, 1, 0, 0, 0, 1], configsku2 : [0, 1, 0, 1, 0, 0], ...}

        usage:
            sku_color_features = configsku_color_dict(env)
    ''' 

    try:
        color_dict = simpleColor_dict(env)
        conn = connect(env['PostgreSqlConnectParameter'])
        cur = conn.cursor()
        configsku_color_list = []
        sql = "select configurable_sku, color_code from product where category_path <> 'category/materials'"
        cur.execute(sql)
        row = cur.fetchone()
        while row:
            configsku_color_list.append((row[0], row[1]))
            row = cur.fetchone()
        
        sku_color_dict = defaultdict(set)
        for (configsku, color) in configsku_color_list:
            sku_color_dict[configsku].add(color)

        sku_color_features = {}
        for sku in sku_color_dict.keys():
            color_vector = simpleColor_vectors(sku_color_dict[sku], color_dict)
            sku_color_features[sku] = color_vector

        return sku_color_features
    finally:
        print("close connection...")
        conn.close()
