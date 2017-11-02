from . import db

from pony import orm


class Author(db.Entity):
    name = orm.Required(str)
    articles = orm.Set('Article')