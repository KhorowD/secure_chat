import sqlite3
from sqlite3.dbapi2 import Error


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('chat.db')
    except Error:
        print(Error)

    return conn


def setup_db_conn(conn):
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS templates(
        id INTEGER PRIMARY KEY, 
        name VARCHAR(255) UNIQUE NOT NULL,
        template TEXT NOT NULL
    )''')

def create_user(conn, user):
    cur = conn.cursor()
    payload = (user)

def create_template(conn, name, json):
    cur = conn.cursor()
    payload = (name, json)
    cur.execute("INSERT INTO templates (name,template) VALUES (?, ?)", payload)
    conn.commit()


def get_templates(conn):
    cur = conn.cursor()
    cur.execute("SELECT name, template FROM templates")
    return cur.fetchall()


def get_template(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT template FROM templates WHERE name = ?", name)
    return cur.fetchone()
