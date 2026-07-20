import sqlite3
import numpy

DB_PATH = "actors.db"

def get_connection():
    """Return a database connection."""
    return sqlite3.connect(DB_PATH)

def setup_database():
    """Create tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actors (
            actor_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            dob        TEXT,
            nationality TEXT,
            face_encoding BLOB NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS films (
            film_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title   TEXT NOT NULL,
            year    INTEGER,
            genre   TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actor_films (
            actor_id INTEGER,
            film_id  INTEGER,
            role     TEXT,
            PRIMARY KEY (actor_id, film_id),
            FOREIGN KEY (actor_id) REFERENCES actors(actor_id),
            FOREIGN KEY (film_id)  REFERENCES films(film_id)
        )
    """)

    conn.commit()
    conn.close()

def load_all_actor_encodings():
    """Load all actor records with their face encodings from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT actor_id, name, face_encoding FROM actors")
    rows = cursor.fetchall()
    conn.close()

    actors = []
    for row in rows:
        actor_id, name, encoding_blob = row
        encoding = numpy.frombuffer(encoding_blob, dtype=numpy.float64)
        actors.append({"id": actor_id, "name": name, "encoding": encoding})
    return actors

def get_actor_details(actor_id):
    """Retrieve actor personal details by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, dob, nationality FROM actors WHERE actor_id = ?",
        (actor_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return row  # returns (name, dob, nationality) or None

def get_filmography(actor_id):
    """Retrieve all films linked to an actor, ordered by year descending."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT films.title, films.year, films.genre, actor_films.role
        FROM films
        JOIN actor_films ON films.film_id = actor_films.film_id
        WHERE actor_films.actor_id = ?
        ORDER BY films.year DESC
    """, (actor_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"title": r[0], "year": r[1], "genre": r[2], "role": r[3]} for r in rows]

def search_actors_by_name(query):
    """Return actors whose names contain the query string (case-insensitive)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT actor_id, name FROM actors WHERE name LIKE ? LIMIT 10",
        (f"%{query}%",)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows] 