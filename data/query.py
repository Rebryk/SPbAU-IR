from datetime import datetime

import pytz
from pony import orm

from . import db


class Query(db.Entity):
    query = orm.Required(str)
    results_count = orm.Optional(int)
    date = orm.Required(datetime, default=lambda: datetime.now(tz=pytz.timezone("Europe/Moscow")))
