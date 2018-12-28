import psycopg2

def connect(params):
    conn = None
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        print('Connected...\n')
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        conn.close()