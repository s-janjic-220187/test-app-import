import os
import mysql.connector

DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'db'),
    'port': int(os.environ.get('MYSQL_PORT', 3306)),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'root'),
    'database': os.environ.get('MYSQL_DATABASE', 'python_dev')
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
