import psycopg2.pool

class Database:
    def __init__(self, app):
        self.db_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=app.config['DB_HOST'],
            port=app.config['DB_PORT'],
            dbname=app.config['DB_NAME'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD']
        )

    def get_conn(self):
        return self.db_pool.getconn()

    def put_conn(self, conn):
        self.db_pool.putconn(conn)
