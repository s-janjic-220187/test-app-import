from flask import Flask, render_template, request, jsonify, redirect, url_for
import mysql.connector
import xml.etree.ElementTree as ET
import io
import subprocess

# Update these with your MariaDB credentials
DB_CONFIG = {
    'host': 'db',  # Use Docker Compose service name
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'python_dev'
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
        zip=zip
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
@app.route('/api/events/<int:event_id>', methods=['PUT', 'DELETE'])
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
    else:
        cur.execute("SELECT id, title, event_type, event_date FROM events")
        events = cur.fetchall()
        cur.close()
        conn.close()
        # FullCalendar expects [{title, start, ...}]
        return jsonify([
            {
                'id': e['id'],
                'title': f"{e['title']} ({e['event_type']})",
                'start': e['event_date'],
                'event_type': e['event_type']
            } for e in events
        ])

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

if __name__ == '__main__':
    app.run(debug=True)

