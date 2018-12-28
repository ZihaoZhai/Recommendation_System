import psycopg2
from connection import connect

def fetch_category(env):
    try:
        conn = connect(env['PostgreSqlConnectParameter'])
        cur = conn.cursor()
        category = {}
        uniqId = 0
        sql = "select distinct category_path from product where category_path <> 'category/materials' or category_path is null"
        cur.execute(sql)
        row = cur.fetchone()
        while row:
            if row[0] and row[0] not in category:
                category[row[0]] = uniqId
                uniqId += 1
            row = cur.fetchone()
        return category
    finally:
        print("close connection...")
        conn.close()

def encode_category(category, category_dict):

    res = [0 for _ in range(len(category_dict))]
    if not category:
        return res
    
    res[category_dict[category]] = 1    
    return res


def configsku_category_dict(env):
    try:
        conn = connect(env['PostgreSqlConnectParameter'])
        cur = conn.cursor()
        sql = "select configurable_sku, category_path from product where category_path <> 'category/materials' or category_path is null"
        cur.execute(sql)
        row = cur.fetchone()
        category_dict = fetch_category(env)
        sku_category = dict()
        while row:
            sku_category[row[0]] = encode_category(row[1], category_dict)
            row = cur.fetchone()

        return sku_category

    finally:
        print("close connection...")
        conn.close()
