import psycopg2
from connection import connect
import numpy as np



def price_range(env):
    conn = connect(env['PostgreSqlConnectParameter'])
    cur = conn.cursor()
    sql = "select price from product where category_path <> 'category/materials'"
    prices = []
    cur.execute(sql)
    row = cur.fetchone()
    while row:
        prices.append(float(row[0]))
        row = cur.fetchone()
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