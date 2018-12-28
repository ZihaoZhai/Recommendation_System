import psycopg2
from connection import connect
#Add filter Style
def fetch_filterStyle(env):
    conn = connect(env['PostgreSqlConnectParameter'])
    cur = conn.cursor()
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
    if not filterStyle:
        return res
    styles = filterStyle.split(',')
    styles = [x for s in styles for x in s.split('&')]
    for style in styles:
        if style.strip() in style_dict.keys():
            res[style_dict[style.strip()]] = 1
        
    return res