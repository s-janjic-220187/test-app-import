from flask import Flask, render_template, request, jsonify, redirect, url_for
import mysql.connector
import xml.etree.ElementTree as ET
import io
import subprocess
import os
import re
import logging
import sys

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

# Update these with your MariaDB credentials
DB_CONFIG = {
    'host': get_env('MYSQL_HOST', 'MYSQLHOST', default=db_url_config.get('host', 'db')),
    'port': int(get_env('MYSQL_PORT', 'MYSQLPORT', default=db_url_config.get('port', 3306))),
    'user': get_env('MYSQL_USER', 'MYSQLUSER', default=db_url_config.get('user', 'root')),
    'password': get_env('MYSQL_PASSWORD', 'MYSQLPASSWORD', default=db_url_config.get('password', 'root')),
    'database': get_env('MYSQL_DATABASE', 'MYSQLDATABASE', default=db_url_config.get('database', 'python_dev'))
}

def ensure_events_table():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            event_type ENUM('Rodjendan', 'Slava', 'Veselje') NOT NULL,
            event_date DATE NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# Run DB migrations before anything else
try:
    subprocess.run(['python', 'migrations/migrate.py'], check=True)
except Exception as e:
    print('Migration failed:', e)

# Ensure events table exists before app is created
try:
    ensure_events_table()
except Exception:
    pass

app = Flask(__name__)

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/users')
def show_users():
    table = request.args.get('table', 'user')
    sort = request.args.get('sort', 'first_name')
    direction = request.args.get('direction', 'asc')
    if direction not in ['asc', 'desc']:
        direction = 'asc'
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table} LIMIT 1")
        first_row = cursor.fetchone()  # fetch one row to clear the result
        col_names_raw = [desc[0] for desc in cursor.description] if cursor.description else []
        col_names = [col.replace('_', ' ').title() for col in col_names_raw]
        if sort not in col_names_raw:
            sort = col_names_raw[0] if col_names_raw else 'first_name'
        cursor.execute(f"SELECT * FROM {table} ORDER BY {sort} {direction}")
        names = cursor.fetchall()
        col_count = len(names[0]) if names else 0
    except Exception as e:
        names = []
        col_names = []
        col_names_raw = []
        col_count = 0
    cursor.close()
    conn.close()
    return render_template(
        'users.html',
        names=names,
        col_count=col_count,
        col_names=col_names,
        col_names_raw=col_names_raw,
        table=table,
        sort=sort,
        direction=direction,
        zip=zip,
        editable=(table == 'test_user')
    )

@app.route('/import', methods=['GET', 'POST'])
def import_users():
    if request.method == 'GET':
        return render_template('import.html')
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    file = request.files['file']
    if not file or not file.filename.endswith('.xml'):
        return jsonify({'success': False, 'error': 'Invalid file type'})
    try:
        xml_data = file.read()
        tree = ET.parse(io.BytesIO(xml_data))
        root = tree.getroot()
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Drop test_user table if it exists
        cur.execute("DROP TABLE IF EXISTS test_user")
        # Create test_user table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS test_user (
                id INT PRIMARY KEY,
                first_name VARCHAR(50),
                middle_name VARCHAR(50),
                last_name VARCHAR(50),
                date_of_birth DATE,
                created_on DATETIME,
                is_active TINYINT
            )
        """)
        # Delete all existing data from test_user
        cur.execute("DELETE FROM test_user")
        # Import data from XML
        for user in root.findall('user'):
            user_id = int(user.find('id').text)
            first_name = user.find('first_name').text
            middle_name = user.find('middle_name').text
            last_name = user.find('last_name').text
            date_of_birth = user.find('date_of_birth').text
            created_on = user.find('created_on').text
            is_active = int(user.find('is_active').text)
            cur.execute("""
                INSERT INTO test_user (id, first_name, middle_name, last_name, date_of_birth, created_on, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, first_name, middle_name, last_name, date_of_birth, created_on, is_active))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/events')
def events_page():
    return render_template('events.html')

@app.route('/api/events', methods=['GET', 'POST'])
@app.route('/api/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE'])
def api_events(event_id=None):
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)
    if request.method == 'POST':
        data = request.get_json()
        cur.execute(
            "INSERT INTO events (title, event_type, event_date) VALUES (%s, %s, %s)",
            (data['title'], data['event_type'], data['event_date'])
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    elif request.method == 'PUT' and event_id is not None:
        data = request.get_json()
        cur.execute(
            "UPDATE events SET title=%s, event_type=%s, event_date=%s WHERE id=%s",
            (data['title'], data['event_type'], data['event_date'], event_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    elif request.method == 'DELETE' and event_id is not None:
        cur.execute("DELETE FROM events WHERE id=%s", (event_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    elif request.method == 'GET' and event_id is not None:
        cur.execute("SELECT id, title, event_type, event_date FROM events WHERE id=%s", (event_id,))
        event = cur.fetchone()
        cur.close()
        conn.close()
        if event:
            return jsonify({
                'id': event['id'],
                'title': event['title'],
                'event_type': event['event_type'],
                'event_date': str(event['event_date'])
            })
        else:
            return jsonify({'error': 'Event not found'}), 404
    else:
        # Accept and log query params for debugging
        start = request.args.get('start')
        end = request.args.get('end')
        print(f"/api/events called with start={start}, end={end}")
        # Fetch events from events table
        cur.execute("SELECT id, title, event_type, event_date FROM events")
        events = cur.fetchall()
        # Fetch all user birthdays
        cur.execute("SELECT id, first_name, last_name, date_of_birth FROM user")
        users = cur.fetchall()
        print('API /api/events returning:', events)
        cur.close()
        conn.close()
        type_colors = {'Rodjendan': '#ff8a00', 'Slava': '#2575fc', 'Veselje': '#e52e71'}
        # Convert user birthdays to events
        user_birthday_events = [
            {
                'id': f'user-{u["id"]}',
                'title': f'{u["first_name"]} {u["last_name"]}',
                'start': str(u['date_of_birth']),
                'event_type': 'Rodjendan',
                'color': type_colors['Rodjendan']
            } for u in users if u['date_of_birth']
        ]
        # Convert regular events
        db_events = [
            {
                'id': e['id'],
                'title': e['title'],
                'start': str(e['event_date']),
                'event_type': e['event_type'],
                'color': type_colors.get(e['event_type'], '#2575fc')
            } for e in events
        ]
        return jsonify(user_birthday_events + db_events)

@app.route('/sync_users_to_events')
def sync_users_to_events():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)
    # Get all users
    cur.execute("SELECT id, first_name, last_name, date_of_birth FROM user")
    users = cur.fetchall()
    # Get all existing rodjendan events (by title and date)
    cur.execute("SELECT title, event_date FROM events WHERE event_type='Rodjendan'")
    existing = {(e['title'], str(e['event_date'])) for e in cur.fetchall()}
    added = 0
    for u in users:
        title = f"{u['first_name']} {u['last_name']}"
        date = str(u['date_of_birth'])
        if (title, date) not in existing:
            cur.execute(
                "INSERT INTO events (title, event_type, event_date) VALUES (%s, %s, %s)",
                (title, 'Rodjendan', date)
            )
            added += 1
    conn.commit()
    cur.close()
    conn.close()
    return f'Synced {added} rodjendan events from users.'

@app.route('/api/user/<int:user_id>', methods=['GET', 'PUT'])
def api_user(user_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)
    if request.method == 'GET':
        cur.execute("SELECT * FROM user WHERE id=%s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            # Format date_of_birth as YYYY-MM-DD for input type="date"
            dob = user.get('date_of_birth')
            if dob:
                user['date_of_birth'] = str(dob)[:10]
            return jsonify(user)
        else:
            return jsonify({'error': 'User not found'}), 404
    elif request.method == 'PUT':
        data = request.get_json()
        cur.execute("""
            UPDATE user SET first_name=%s, middle_name=%s, last_name=%s, date_of_birth=%s, is_active=%s
            WHERE id=%s
        """, (
            data.get('first_name'),
            data.get('middle_name'),
            data.get('last_name'),
            data.get('date_of_birth'),
            data.get('is_active', 1),
            user_id
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})

@app.route('/api/edit_test_user', methods=['POST'])
def edit_test_user():
    data = request.get_json()
    id = data.get('id')
    col = data.get('col')
    value = data.get('value')
    if not id or not col:
        return jsonify({'success': False, 'error': 'Missing id or column'})
    if col not in ['first_name', 'middle_name', 'last_name', 'date_of_birth', 'created_on', 'is_active']:
        return jsonify({'success': False, 'error': 'Invalid column'})
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        cur.execute(f"UPDATE test_user SET {col}=%s WHERE id=%s", (value, id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        cur.close()
        conn.close()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/migrate_imported_users')
def migrate_imported_users():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    # Overwrite all users in user table with those from test_user
    cur.execute("DELETE FROM user")
    cur.execute("SELECT * FROM test_user")
    test_users = cur.fetchall()
    cur.execute("SHOW COLUMNS FROM test_user")
    columns = [col[0] for col in cur.fetchall()]
    for user in test_users:
        user_dict = dict(zip(columns, user))
        cur.execute("INSERT INTO user (id, first_name, middle_name, last_name, date_of_birth, created_on, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (user_dict['id'], user_dict['first_name'], user_dict['middle_name'], user_dict['last_name'], user_dict['date_of_birth'], user_dict['created_on'], user_dict['is_active']))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('show_users', table='user'))

@app.route('/log')
def log_page():
    return render_template('log.html')

@app.route('/stream_log')
def stream_log():
    def generate():
        import time
        logfile = 'app.log'
        try:
            with open(logfile, 'r') as f:
                f.seek(0, 2)  # Go to end of file
                while True:
                    line = f.readline()
                    if line:
                        yield f'data: {line}\n\n'
                    else:
                        time.sleep(1)
        except Exception as e:
            yield f'data: Log file not found or error: {e}\n\n'
    return app.response_class(generate(), mimetype='text/event-stream')

@app.route('/test')
def test_page():
    return render_template('test.html')

@app.route('/run_tests', methods=['POST'])
def run_tests():
    import subprocess
    try:
        # Use verbose output and show summary, test names, and short log
        result = subprocess.run([
            'pytest', 'tests', '--maxfail=1', '--disable-warnings', '-v', '--tb=short', '--show-capture=log', '--durations=10', '--summary', '--color=yes'
        ], capture_output=True, text=True, timeout=30)
        output = result.stdout + '\n' + result.stderr
        success = result.returncode == 0
    except Exception as e:
        output = str(e)
        success = False
    return {'success': success, 'output': output}

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ],
    force=True  # Ensure handlers are replaced and logs are flushed immediately
)
# Ensure Flask's logger uses the same handlers and level
app.logger.handlers = logging.getLogger().handlers
app.logger.setLevel(logging.INFO)

if __name__ == '__main__':
    app.run(debug=True)

