import json

from web import app
from flask import render_template, request, jsonify


@app.route("/")
def search_page():
    return render_template("index.html")


@app.route('/search', methods=['POST'])
def get_counts():
    data = json.loads(request.data.decode())

    query = data["q"]
    from_date = data.get("from", "")
    to_date = data.get("to", "")

    # TODO: calculate results here

    results = []

    # TODO: fill results
    # Document structure: (query_id, rank, id, title, link, date, author, abstract)

    return jsonify(results)
