import psycopg2

def connect(params):
    conn = None
    try:
        conn = psycopg2.connect(**params)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        conn.close()