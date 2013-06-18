import datetime
from google.appengine.ext import db


class User(db.Model):
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    address = db.StringProperty()
    postal_code = db.IntegerProperty()
    institute = db.StringProperty()
    faculty = db.StringProperty()
    course = db.StringProperty()
    hp_num = db.PhoneNumberProperty()
    hp_num_vis = db.BooleanProperty(default=True)
    home_num = db.PhoneNumberProperty()
    home_num_vis = db.BooleanProperty(default=True)
    rating = db.IntegerProperty(default=0)
    prof_complete = db.BooleanProperty(default=False)
    last_active = db.DateTimeProperty(default=datetime.datetime.now())

class Book(db.Model):
    module_code = db.StringProperty()
    title = db.StringProperty()
    author = db.StringProperty()
    publisher = db.StringProperty()
    edition = db.IntegerProperty()
    condition = db.IntegerProperty()
    comment = db.StringProperty()
    cost = db.IntegerProperty()