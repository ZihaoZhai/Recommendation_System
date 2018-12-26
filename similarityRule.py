import psycopg2
import collections
import json
from tqdm import tqdm
import pandas as pd
import numpy as np

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

#Add price 
def price_range(env, prices):
    interval = env["similarityRulesParameter"]["price_intervals"]
    ratio = env["similarityRulesParameter"]["price_filterRatio"]
    filter_prices = [ele for ele in prices if ele >= 1 and ele < 20000]
    l = len(filter_prices)
    filter_prices = sorted(filter_prices)
    rangePrice = (filter_prices[int(ratio * l)] - filter_prices[0]) / interval
    res = []
    for i in range(1, interval):
        res.append(np.floor(i * rangePrice))
    return res

def add_price(price, priceInterval):
    '''
        input : 
            price : price of item
            priceInterval : price range to put item in.
        
        return:
            0-1 vector to desecribe where to put item.
            
    '''
    L = len(priceInterval)
    res = [0 for i in range(L)]
    i = 0
    while i < L:
        if priceInterval[i] > price:
            res[i] = 1
            break
        i += 1
    if i == L:
        res[L - 1] = 1
    return res

#Add simple color
def fetch_simpleColors(cur):
    colors = []
    sql = "select simple_color from product where category_path <> 'category/materials'"
    cur.execute(sql)
    row = cur.fetchone()
    while row:
        colors.append(row[0])
        row = cur.fetchone()
    colors = list(map(lambda x : 'Mix' if x == 'Mixed Colors' else x, colors))
    colors = list(map(lambda x : 'Mix' if x == 'Mix Colors' else x, colors))
    colors = list(map(lambda x : 'Mix' if x == 'Mix Of Colors' else x, colors))
    
    return colors
    
    
def simpleColor_dict(colors):
    simpleColor_dict = {}
    uniqId = 0
    for color in colors:
        if color not in simpleColor_dict.keys() and color != None:
            simpleColor_dict[color] = uniqId
            uniqId += 1
    return simpleColor_dict
    
    
def add_simpleColor(simpleColor, color_dict):
    '''
        input: 
            color : The color to transform
            color_dict : color-number dictionary
        
        return:
            encoding vector for given color.
    '''
    uniqKeys = list(color_dict.keys())
    encoding_vec = [0 for _ in range(len(uniqKeys))]
    encoding_vec[color_dict[simpleColor]] = 1
    
    return encoding_vec



#Add brightness
def fetch_colors(cur):
    colors = []
    sql = "select color from product where category_path <> 'category/materials'"
    cur.execute(sql)
    row = cur.fetchone()
    while row:
        colors.append(row[0].split('/')[0])
        row = cur.fetchone()
    
    return colors


def add_brightness(color):
    '''
        Add brightness feature to the item
        input :
            color : color of item
        output:
            brightness encoding category it belongs to.
            'Light', 'Dark' or else.
            [1,0,0]  [0,0,1]   [0,1,0]
    '''
    res = [0, 0, 0]
    if color == None:
        return res
    if color.find('Light') != -1:
        res[0] = 1
    elif color.find('Dark') != -1:
        res[2] = 1
    else:
        res[1] = 1
        
    return res



#Add filter brand:
def add_filterBrands(filterBrand):
    '''
        add filter brand feature to data.
        input:
            filterBrand of data.
        
        return:
            encoding vector for filter brand feature.
    '''
    brand_dict = {'Black Label': 0, "Eve by Eve's": 1, 'Pink Label': 2}
    res = [0, 0, 0]
    res[brand_dict[filterBrand]] = 1
    return res


#Add filter Style
def fetch_filterStyle(cur):
    filter_style = {}
    uniqId = 0
    sql = "select distinct filterstyle from product where category_path <> 'category/materials' or category_path is null"
    cur.execute(sql)
    row = cur.fetchone()
    while row:
        if row[0] is None or len(row[0]) == 0:
            if 'None' not in filter_style.keys():
                filter_style['None'] = uniqId
                uniqId += 1
        else:
            styles = row[0].split(',')
            styles = [x for s in styles for x in s.split('&')]
            for style in styles:
                if style.strip() not in filter_style.keys():
                    filter_style[style.strip()] = uniqId
                    uniqId += 1
        row = cur.fetchone()
    return filter_style


def add_filterStyle(filterStyle, style_dict):
    res = [0 for _ in range(len(style_dict))]
    styles = filterStyle.split(',')
    styles = [x for s in styles for x in s.split('&')]
    for style in styles:
        if style.strip() in style_dict.keys():
            res[style_dict[style.strip()]] = 1
        
    return res

def main():
    with open('env.json') as f:
        env = json.loads(f.read())
        
    cur = connect(env['basicRulesParameter']['PostgreSqlConnectParameter'])
    sql = "select price, color, simple_color, filterbrand, filterstyle from product \
       where category_path <> 'category/materials' or category_path is null"
    cur.execute(sql)
    row = cur.fetchone()

    priceInterval = price_range(env, prices)
    simple_colors = fetch_simpleColors(cur)
    color_dict = simpleColor_dict(simple_colors)
    style_dict = fetch_filterStyle(cur)

    while row:
        price = float(row[0])
        color = row[1]
        simple_color = row[2]
        brand = row[3]
        filterStyle = row[4]
        
        price_vector = add_price(price, priceInterval)
        simpleColor_vector = add_simpleColor(simple_color, color_dict)
        brightness_vector = add_brightness(color)
        brand_vector = add_filterBrands(brand)
        style_vector = add_filterStyle(filterStyle, style_dict)
        
        print('price_vector : ', price_vector)
        print('price : ', price)
        print('simpleColor_vector : ', simpleColor_vector)
        print('simple_color : ', simple_color)
        print('brightness_vector : ', brightness_vector)
        print('color : ', color)
        print('brand_vector : ', brand_vector)
        print('brand : ', brand)
        print('style_vector : ', style_vector)
        print('filterStyle : ', filterStyle)
        
        row = cur.fetchone()

if __name__ == '__main__':
    main()

class Item :
    '''
        Item class that is used to calculate similarity among different items
    '''
    def __init__(self, env, price, color, simple_color, brand, filterStyle):
        self.price = price
        self.color = color
        self.simple_color = simple_color
        self.brand = brand
        self.filterStyle = filterStyle
        if env['similarityRulesParameter']['usePrice']:
            priceInterval = price_range(env, prices)
            self.price_vector = add_price(price, priceInterval)
        
        if env['similarityRulesParameter']['useBrightness']:
            self.brightness_vector = add_brightness(color)
        
        if env['similarityRulesParameter']['useSimpleColor']:
            color_dict = simpleColor_dict(simple_color)
            self.color_vector =  add_simpleColor(simple_color, color_dict)
        
        if env['similarityRulesParameter']['useBrand']:
            self.brand_vector = add_filterBrands(brand)
        
        if env['similarityRulesParameter']['useFilterStyle']:
            style_dict = fetch_filterStyle(cur)
            self.style_vector = add_filterStyle(filterStyle, style_dict)

    def Jacard_similarity(self, vec1, vec2):
        if vec1 is None or vec2 is None or len(vec1) != len(vec2):
            return 0
        return float(sum([i for i in range(len(vec1)) if vec1[i] == vec2[i] and vec1[1] == 1])) / \
               sum([i for i in range(len(vec1)) if vec1[i] == 1 or vec2[1] == 1])

    def Cosint_similarity(self, vec1, vec2):
        pass

    def calculate_similarity(self, vec1, vec2):
        pass
        

    def price_similarity(self, item):
        return self.calculate_similarity(self.price_vector, item.price_vector)

    def color_similarity(self, item):
        return self.calculate_similarity(self.color_vector, item.color_vector)

    def brightness_similarity(self, item):
        return self.calculate_similarity(self.brightness_vector, item.brightness_vector)

    def brand_similarity(self, item):
        return self.calculate_similarity(self.brand_vector, item.brand_vector)

    def style_similarity(self, item):
        return self.calculate_similarity(self.style_vector, item.style_vector)
