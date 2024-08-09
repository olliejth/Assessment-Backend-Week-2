"""An API for handling marine experiments."""

from datetime import datetime

from flask import Flask, jsonify, request
from psycopg2 import sql
from psycopg2 import connect, extensions, extras

from database_functions import get_db_connection


app = Flask(__name__)

"""
For testing reasons; please ALWAYS use this connection. 
- Do not make another connection in your code
- Do not close this connection
"""
conn = get_db_connection("marine_experiments")

#########    FUNCTIONS    #########


def get_cursor(connection: extensions.connection) -> extensions.cursor:
    """Reusable function for getting a database cursor."""
    return connection.cursor(cursor_factory=extras.RealDictCursor)


@app.get("/")
def home():
    """Returns an informational message."""
    return jsonify({
        "designation": "Project Armada",
        "resource": "JSON-based API",
        "status": "Classified"
    })


@app.route("/subject", methods=["GET"])
def get_subjects():
    cur = get_cursor(conn)

    cur.execute("""
                SELECT su.subject_id, su.subject_name, sp.species_name, su.date_of_birth
                FROM subject as su
                JOIN species as sp
                ON su.species_id = sp.species_id
                ORDER BY su.date_of_birth DESC;
                """)

    subjects = cur.fetchall()
    cur.close()

    for s in subjects:
        date_str = s["date_of_birth"].strftime("%Y-%m-%d")
        s["date_of_birth"] = date_str

    return jsonify(subjects), 200


if __name__ == "__main__":
    app.config["DEBUG"] = True
    app.config["TESTING"] = True

    app.run(port=8000, debug=True)

    conn.close()
