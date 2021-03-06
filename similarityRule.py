import psycopg2
import json
import numpy as np
from collections import defaultdict
from datetime import datetime
import sys

sys.path.append('./featureExtractor/')
from connection import connect
from color_features import configsku_color_dict
from price_features import price_range, add_price
from filterStyle_features import fetch_filterStyle, add_filterStyle
from category_features import configsku_category_dict

class Item :
    def __init__(self, env, row,\
                 priceInterval, style_dict, sku_color_dict, sku_category_dict):
        self.env = env
        self.row = row
        self.price = float(row[0])
        self.filterStyle = row[1]
        self.category_path = row[2]
        self.configsku = row[3]
        self.sku_color_dict = sku_color_dict
        self.sku_category_dict = sku_category_dict
        if env['similarityRulesParameter']['usePrice']:
            self.price_vector = add_price(self.price, priceInterval)
        
        if env['similarityRulesParameter']['useSimpleColor']:
            self.color_vector = self.sku_color_dict[self.configsku]
        
        if env['similarityRulesParameter']['useFilterStyle']:
            self.style_vector = add_filterStyle(self.filterStyle, style_dict)

        if env['similarityRulesParameter']['useCategory']:
            self.category_vector = self.sku_category_dict[self.configsku]

    def Jacard_similarity(self, vec1, vec2):
        if vec1 is None or vec2 is None or len(vec1) != len(vec2):
            return 0
        denominator = 0
        for i in range(len(vec1)):
            if vec1[i] == 1 and vec2[i] == 1:
                denominator += 2
            elif vec1[i] == 1 or vec2[i] == 1:
                denominator += 1
        if denominator == 0:
            return 0
        return float(sum([1 for i in range(len(vec1)) if vec1[i] == vec2[i] and vec1[1] == 1])) / denominator

    def Cosine_similarity(self, vec1, vec2):
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return 0 if sum(vec1) == 0 or sum(vec2) == 0 else float(vec1.dot(vec2)) / (sum(vec1) * sum(vec2))

    def calculate_similarity(self, vec1, vec2):
        if self.env['similarityRulesParameter']['similarity_metric'] == 'cosine':
            return self.Cosine_similarity(vec1, vec2)
        else:
            return self.Jacard_similarity(vec1, vec2)

    def price_similarity(self, item):
        return self.calculate_similarity(self.price_vector, item.price_vector)

    def color_similarity(self, item):
        return self.calculate_similarity(self.color_vector, item.color_vector)

    def style_similarity(self, item):
        return self.calculate_similarity(self.style_vector, item.style_vector)

    def category_similarity(self, item):
        return self.calculate_similarity(self.category_vector, item.category_vector)

    def subfield_similarity(self, item, start, end):
        intersection = 0
        union = 0

        for i in range(start, end):
            if self.row[i] and self.row[i] == item.row[i]:
                intersection += 1
                union += 1
            elif self.row[i] and item.row[i]:
                union += 2
            elif self.row[i] or item.row[i]:
                union += 1

        if union == 0:
            return 0
        return float(intersection) / union

    def bra_similarity(self, item):
        return self.subfield_similarity(item, 4, 17)

    def panty_similarity(self, item):
        return self.subfield_similarity(item, 17, 20)

    def lingerie_similarity(self, item):
        return self.subfield_similarity(item, 20, 27)

    def beauty_similarity(self, item):
        return self.subfield_similarity(item, 27, 30)


    def similarity(self, item,env):
        return env['priceWeight'] * self.price_similarity(item) + \
               env['colorWeight'] * self.color_similarity(item) + \
               env['styleWeight'] * self.style_similarity(item) + \
               env['categoryWeight'] * self.category_similarity(item) + \
               env['braTypeSimilarity'] * self.bra_similarity(item) + \
               env['pantyTypeWeight'] * self.panty_similarity(item) + \
               env['lingerieTypeWeight'] * self.lingerie_similarity(item) + \
               env['beautyTypeSimilarity'] * self.beauty_similarity(item)

def get_similarity_dict(env):
    print('Connecting to the PostgreSQL database...')
    print('Connected...\n')
    conn = connect(env['PostgreSqlConnectParameter'])
    cur = conn.cursor()
    sql = " select price, filterstyle, category_path, configurable_sku, \
                   bra_type, bra_by_function, bra_padding_level, bra_padding_style, \
                   bra_wire_style, bra_strap, bra_wear_style, bra_neck_style, \
                   bra_closure, bra_shape, bra_seam, bra_back_style, \
                   bra_smooth_level, \
                   panty_style, panty_cut, panty_smooth_level, \
                   lingerie_product_type, clothing_by_function, sleeve_length, \
                   pant_length, dress_length, dress_knee_length, collar_shape, \
                   beauty_type, makeup_product_type, skincare_product_type \
            from product\
            where category_path <> 'category/materials' or category_path is null"
    cur.execute(sql)
    item_list = []
    visited = set()
    row = cur.fetchone()
    priceInterval = price_range(env) # transform price into ranges feature
    style_dict = fetch_filterStyle(env) # get {filterStyle : uniqId} dictionary
    sku_color_dict = configsku_color_dict(env) # get {configsku : color_set} dctionary
    sku_category_dict = configsku_category_dict(env) # get {configsku : category} dctionary
    while row:
        configsku = row[3]
        if configsku in visited:
            row = cur.fetchone()
            continue
        item_list.append(Item(env, row,\
                              priceInterval, style_dict, sku_color_dict, sku_category_dict))
        visited.add(configsku)
        row = cur.fetchone()
    

    print 'Calculating similarity...'
    start=datetime.now()
    count=0
    item_similarity_dict = defaultdict(dict)
    for i in range(len(item_list)):
        item1 = item_list[i]
        for j in range(i + 1, len(item_list)):
            item2 = item_list[j]
            similarity = item1.similarity(item2,env['similarityRulesParameter'])
            if similarity >= env['similarityRulesParameter']['similarity_threshold']:
                item_similarity_dict[item1.configsku][item2.configsku] = similarity
                item_similarity_dict[item2.configsku][item1.configsku] = similarity
        count+=1
        if count%100==0:
            print int(count/float(len(item_list))*100),'%','finished',datetime.now()-start
    item_similarity_dict = dict(item_similarity_dict)
    conn.close()
    return item_similarity_dict



