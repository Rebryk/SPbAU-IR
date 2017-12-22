import json
import logging
from datetime import datetime

import matplotlib.pyplot as plt
from flask import render_template, request, jsonify
from pony.orm import select, db_session, commit

from data import Article, Query, Like
from doc2vec import Doc2VecModel
from index import InvertedIndex
from ranker import TfIdf, AbstractAndArticle
from text_processing import TextProcessor
from web import app

INDEX_FOLDER = "index"
TOP_COUNT = 20
TOP_COUNT_RESULT = 5
VECTORS_PER_FILE = 512
VECTORS_SAVE_FOLDER = "ranker"

ranker = None
logger = logging.getLogger(__name__)

model = Doc2VecModel.load_model("doc2vec/model.dump")


def _read_file(path):
    with open(path, "r") as file:
        return " ".join(file.readlines())


def parse_date(date, format_="%d.%m.%Y"):
    try:
        return datetime.strptime(date, format_)
    except Exception as e:
        logger.debug("Failed to parse date: {}".format(str(e)))
        return None


def in_date_range(date, from_date, to_date):
    if from_date and date < from_date:
        return False

    if to_date and date > to_date:
        return False

    return True


def draw_map(query_id, ids):
    x, y = [], []

    fig, ax = plt.subplots(nrows=1, ncols=1)

    for vec in model.vecs2d.values():
        x.append(vec[0])
        y.append(vec[1])

    ax.scatter(x, y, s=1)
    for vec_id in ids:
        vec = model.vecs2d[vec_id]
        ax.scatter(vec[0], vec[1])

    # query_text

    #fig.savefig("images/{}.png".format(query_id))
    fig.savefig("web/static/index.png")



@db_session
def setup_ranker():
    global ranker

    text_processor = TextProcessor()
    docs = []
    index = InvertedIndex.load(INDEX_FOLDER, "inverted_index")
    articles = select(article.id for article in Article)
    for article_id in articles:
        article = Article[article_id]
        docs.append(AbstractAndArticle(article, _read_file(article.processed_abstract_path)))

    ranker = TfIdf(index, text_processor, docs, VECTORS_PER_FILE, VECTORS_SAVE_FOLDER)


@app.route("/like", methods=['POST'])
@db_session
def like_document():
    data = json.loads(request.data.decode())

    query_id = int(data["query_id"])
    rank = int(data["rank"])
    relevance = int(data["relevance"])

    Like(query_id=query_id, rank=rank, relevance=relevance)
    return "", 200


@app.route("/")
def search_page():
    return render_template("index.html")


@app.route('/search', methods=['POST'])
@db_session
def get_counts():
    data = json.loads(request.data.decode())

    query_text = data["q"]
    from_date = parse_date(data.get("from", ""))
    to_date = parse_date(data.get("to", ""))

    query = Query(query=query_text)
    commit()

    top_ids = ranker.rank(query_text, TOP_COUNT)

    # Document structure: (query_id, rank, id, title, link, date, author, abstract)
    results = []

    for rank, article_id in enumerate(top_ids):
        article = Article[article_id]

        if not in_date_range(article.date, from_date, to_date):
            continue

        authors = ", ".join([author.name for author in article.authors])

        # read initial abstract
        with open(article.abstract_path, "r") as f:
            abstract = f.read()

        results.append({
            "query_id": query.id,
            "rank": rank,
            "id": article.id,
            "title": article.title,
            "link": article.link_to_pdf,
            "date": article.date.strftime("%d %b %Y"),
            "author": authors,
            "abstract": abstract
        })

    results = results[:TOP_COUNT_RESULT]
    query.results_count = len(results)

    draw_map(query.id, set(map(lambda it: it["id"], results)))

    return jsonify(results)


setup_ranker()
