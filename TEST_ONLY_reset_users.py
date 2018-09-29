from geektext.models import *
from geektext import db

users = User.query.all()
for u in users:
    db.session.delete(u)
