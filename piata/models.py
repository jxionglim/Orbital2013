import datetime
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.db import djangoforms
from django import forms

class User(db.Model):
    first_name = db.StringProperty(default="")
    last_name = db.StringProperty(default="")
    address = db.StringProperty(default="")
    postal_code = db.StringProperty(default="")
    hp_num = db.StringProperty(default="")
    hp_num_hide = db.BooleanProperty(default=False)
    home_num = db.StringProperty(default="")
    home_num_hide = db.BooleanProperty(default=False)
    institute = db.StringProperty(default="")
    faculty = db.StringProperty(default="")
    course = db.StringProperty(default="")
    rating = db.IntegerProperty(default=0)
    prof_complete = db.BooleanProperty(default=False)
    last_active = db.DateTimeProperty(default=datetime.datetime.now())

class UserForm(djangoforms.ModelForm):
    first_name = forms.CharField(label="First Name:",help_text="testing")

class Book(db.Model):
    module_code = db.StringProperty()
    title = db.StringProperty()
    author = db.StringProperty()
    publisher = db.StringProperty()
    edition = db.IntegerProperty()
    condition = db.IntegerProperty()
    comment = db.StringProperty()
    cost = db.IntegerProperty()