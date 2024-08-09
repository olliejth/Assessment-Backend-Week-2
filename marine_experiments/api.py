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


def is_valid_type(e_type: str) -> bool:
    if isinstance(e_type, str) and e_type.lower() in ("intelligence", "obedience", "aggression"):
        return True
    return False


def is_valid_score_over(e_score: int) -> bool:
    if isinstance(e_score, int) and e_score >= 0 and e_score <= 100:
        return True
    return False


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
                ORDER BY su.date_of_birth DESC
                ;
                """)

    subjects = cur.fetchall()
    cur.close()

    for s in subjects:
        date_str = s["date_of_birth"].strftime("%Y-%m-%d")
        s["date_of_birth"] = date_str

    return jsonify(subjects), 200


@app.route("/experiment", methods=["GET"])
def get_experiments():
    type = request.args.get("type")
    score_over = request.args.get("score_over")
    cur = get_cursor(conn)

    q = """
                SELECT e.experiment_id, su.subject_id, sp.species_name AS "species", e.experiment_date, et.type_name AS "experiment_type", e.score
                FROM subject as su
                JOIN species as sp
                ON su.species_id = sp.species_id
                JOIN experiment as e
                ON su.subject_id = e.subject_id
                JOIN experiment_type as et
                ON e.experiment_type_id = et.experiment_type_id
                """
    if type and not is_valid_type(type):
        return jsonify({"error": "Invalid value for 'type' parameter"}), 400

    if score_over and not is_valid_score_over(score_over):
        return jsonify({"error": "Invalid value for 'score_over' parameter"}), 400

    if not type and not score_over:
        cur.execute(q + " " + "ORDER BY e.experiment_date DESC;")

    if type and is_valid_type(type) and not score_over:
        q += " " + f"WHERE et.type_name = '{type.lower()}'"
        cur.execute(q + " " + "ORDER BY e.experiment_date DESC;")

    if score_over and is_valid_type(score_over) and not type:
        q += " " + f"WHERE e.score > {score_over/10*100}"
        cur.execute(q + " " + "ORDER BY e.experiment_date DESC;")

    experiments = cur.fetchall()
    cur.close()

    for e in experiments:
        e["experiment_date"] = e["experiment_date"].strftime("%Y-%m-%d")

    for e in experiments:
        if e["experiment_type"] == "intelligence":
            e["score"] = f"{round(((e["score"]*100)/30), 2)}%"
        elif e["experiment_type"] == "obedience" or "aggression":
            e["score"] = f"{round(((e["score"]*100)/10), 2)}%"

    return jsonify(experiments), 200


@app.route("/delete/<id>", methods=['DELETE', 'POST', 'PUT'])
def delete_row(id):
    if request.method == 'POST':
        jsonify({"error": "method error"}), 405

    if request.method == 'PUT':
        jsonify({"error": "method error"}), 405

    if id > 11:
        return "result", 404

    if request.method == 'DELETE':
        cur = get_cursor(conn)

        # Execute the delete statement
        id_str = str(id)
        cur.execute(
            "SELECT * FROM experiment WHERE experiment_id = %s;", (id_str,))
        row = cur.fetchone()

        if row is None:
            error_message = f"Unable to locate experiment with ID {id}."
            cur.close()
            return jsonify({"error": error_message}), 404

        cur.execute(
            "DELETE FROM experiment WHERE experiment_id = %s;", (id_str,))

        experiment_date = row.get("experiment_date").strftime("%Y-%m-%d")

        conn.commit()
        cur.close()

        return jsonify({"experiment_id": id, "experiment_date": experiment_date}), 200


# def delete_experiment(id: int):
#     if request.method == 'DELETE':
#         cur = get_cursor(conn)
#         experiment_exists = False

#         cur.execute(
#             f"SELECT * FROM experiment WHERE experiment_id = {id}")

#         if cur.fetchone():
#             experiment = cur.fetchone()
#             experiment_date = experiment.get("experiment_date").strftime(
#                 "%Y-%m-%d")
#             experiment_exists = True

#         if experiment_exists:
#             cur.execute(
#                 f"DELETE FROM experiment WHERE experiment_id = '{id}';")

#             conn.commit()
#             cur.close()
#             return jsonify({"experiment_id": id, "experiment_date": experiment_date}), 200

#         error_message = f"Unable to locate experiment with ID {id}."
#         cur.close()
#         return jsonify({"error": error_message}), 404

if __name__ == "__main__":
    app.config["DEBUG"] = True
    app.config["TESTING"] = True

    app.run(port=8000, debug=True)

    conn.close()
