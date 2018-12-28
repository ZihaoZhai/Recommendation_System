import psycopg2
import collections
import json
import numpy as np
from collections import defaultdict
from tqdm import tqdm
from connection import connect
from color_features import configsku_color_dict
from price_features import price_range, add_price
from filterStyle_features import fetch_filterStyle, add_filterStyle
from category_features import configsku_category_dict

class Item :
    '''
        Item class that is used to calculate similarity among different items

        "select 0price, 1filterstyle, 2category_path, 3configurable_sku, \
                      4bra_type, 5bra_by_function, 6bra_padding_level, 7bra_padding_style, \
                      8bra_wire_style, 9bra_strap, 10bra_wear_style, 11bra_neck_style, \
                      12bra_closure, 13bra_shape, 14bra_seam, 15bra_back_style, \
                      16bra_smooth_level,\
                      17panty_style, 18panty_cut, 19panty_smooth_level,\
                      20lingerie_product_type, 21clothing_by_function, 22sleeve_length,\
                      23pant_length, 24dress_length, 25dress_knee_length, 26collar_shape, \
                      27beauty_type, 28makeup_product_type, 29skincare_product_type, \
                      from product\
               where category_path <> 'category/materials' or category_path is null"
    '''
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
        return float(sum([i for i in range(len(vec1)) if vec1[i] == vec2[i] and vec1[1] == 1])) / \
               sum([i for i in range(len(vec1)) if vec1[i] == 1 or vec2[1] == 1])

    def Cosine_similarity(self, vec1, vec2):
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return 0 if sum(vec1) == 0 and sum(vec2) == 0 else float(vec1.dot(vec2)) / (sum(vec1) * sum(vec2))

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


    def similarity(self, item):
        return 0.2 * self.price_similarity(item) if self.env['similarityRulesParameter']['usePrice'] else 0 + \
               0.2 * self.color_similarity(item) if self.env['similarityRulesParameter']['useSimpleColor'] else 0 + \
               0.2 * self.style_similarity(item) if self.env['similarityRulesParameter']['useFilterStyle'] else 0 + \
               0.1 * self.category_similarity(item) if self.env['similarityRulesParameter']['useCategory'] else 0 + \
               0.3 * self.bra_similarity(item) + \
               0.3 * self.panty_similarity(item) + \
               0.3 * self.lingerie_similarity(item) + \
               0.5 * self.beauty_similarity(item)


def get_similarity_dict(env):
    #cur = connect(env['PostgreSqlConnectParameter'])
    try:
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
            #price = float(row[0])
            #color_code = row[1]
            #filterStyle = row[2]
            #category_path = row[3]
            configsku = row[3]
            if configsku in visited:
                row = cur.fetchone()
                continue
            item_list.append(Item(env, row,\
                                  priceInterval, style_dict, sku_color_dict, sku_category_dict))
            visited.add(configsku)
            row = cur.fetchone()
        
        item_similarity_dict = defaultdict(dict)
        #cnt = 0
        #print(len(item_list))
        for i in tqdm(range(len(item_list))):
            item1 = item_list[i]
            for j in range(i + 1, len(item_list)):
                item2 = item_list[j]
                similarity = item1.similarity(item2)
                if similarity >= 0.5:
                    item_similarity_dict[item1.configsku][item2.configsku] = similarity
                    item_similarity_dict[item2.configsku][item1.configsku] = similarity
                #print(similarity)
            #cnt += 1
            #if cnt >= 5:
            #    break
        item_similarity_dict = dict(item_similarity_dict)
        print(item_similarity_dict)
        return item_similarity_dict

    finally:
        print("close connection...")
        conn.close()



if __name__ == '__main__':
    with open('env.json') as f:
        env = json.loads(f.read())
    # main(env)
    get_similarity_dict(env)



