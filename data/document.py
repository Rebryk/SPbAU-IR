from . import db
from pony import orm
import datetime


class Document(db.Entity):
    url = orm.Required(str)
    file_path = orm.Required(str)
    document_date = orm.Optional(datetime.datetime)
    document_hash = orm.Required(str)
