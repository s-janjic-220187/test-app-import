import xml.etree.ElementTree as ET
import mysql.connector
import tkinter as tk
from tkinter import filedialog

# Parse XML file
root_tk = tk.Tk()
root_tk.withdraw()
file_path = filedialog.askopenfilename(title="Select XML file", filetypes=[("XML files", "*.xml")])
tree = ET.parse(file_path)
root = tree.getroot()

# Connect to MariaDB
conn = mysql.connector.connect(
    user='root',
    password='root',
    host='localhost',
    port=3306,
    database='python_dev'
)
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

# This code will import data from data.xml into the test_user table
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
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, first_name, middle_name, last_name, date_of_birth, created_on, is_active))

conn.commit()
cur.close()
conn.close()