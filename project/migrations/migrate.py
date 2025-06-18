import os
import mysql.connector

def get_env(*names, default=None):
    for name in names:
        v = os.environ.get(name)
        if v is not None:
            return v
    return default

DB_CONFIG = {
    'host': get_env('MYSQL_HOST', 'MYSQLHOST', default='db'),
    'port': int(get_env('MYSQL_PORT', 'MYSQLPORT', default=3306)),
    'user': get_env('MYSQL_USER', 'MYSQLUSER', default='root'),
    'password': get_env('MYSQL_PASSWORD', 'MYSQLPASSWORD', default='root'),
    'database': get_env('MYSQL_DATABASE', 'MYSQLDATABASE', default='python_dev')
}

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__))


def run_migrations():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    for fname in sorted(f for f in os.listdir(MIGRATIONS_DIR) if f.endswith('.sql')):
        with open(os.path.join(MIGRATIONS_DIR, fname), encoding='utf-8') as f:
            sql = f.read()
            cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    run_migrations()
