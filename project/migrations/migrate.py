import os
import re
import mysql.connector

def get_env(*names, default=None):
    for name in names:
        v = os.environ.get(name)
        if v is not None:
            return v
    return default

def parse_database_url(url):
    # Example: mysql://user:pass@host:port/dbname
    m = re.match(r'mysql://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/([^?]+)', url)
    if m:
        return {
            'user': m.group(1),
            'password': m.group(2),
            'host': m.group(3),
            'port': int(m.group(4)) if m.group(4) else 3306,
            'database': m.group(5)
        }
    return {}

db_url = os.environ.get('DATABASE_URL')
db_url_config = parse_database_url(db_url) if db_url else {}

DB_CONFIG = {
    'host': get_env('MYSQL_HOST', 'MYSQLHOST', default=db_url_config.get('host', 'db')),
    'port': int(get_env('MYSQL_PORT', 'MYSQLPORT', default=db_url_config.get('port', 3306))),
    'user': get_env('MYSQL_USER', 'MYSQLUSER', default=db_url_config.get('user', 'root')),
    'password': get_env('MYSQL_PASSWORD', 'MYSQLPASSWORD', default=db_url_config.get('password', 'root')),
    'database': get_env('MYSQL_DATABASE', 'MYSQLDATABASE', default=db_url_config.get('database', 'python_dev'))
}

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__))


def run_migrations():
    print('DB_CONFIG:', DB_CONFIG)  # Debug print for Railway deployment
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
