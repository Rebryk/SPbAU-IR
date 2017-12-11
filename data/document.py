import datetime

from pony import orm

from . import db


class Document(db.Entity):
    url = orm.Required(str)
    file_path = orm.Required(str)
    document_date = orm.Optional(datetime.datetime)
    document_hash = orm.Required(str)
    is_processed = orm.Required(bool, default=False)
    article = orm.Optional("Article")
