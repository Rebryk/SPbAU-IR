from pony import orm

from . import db


class Author(db.Entity):
    name = orm.Required(str)
    articles = orm.Set("Article")