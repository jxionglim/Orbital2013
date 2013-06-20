import datetime
from google.appengine.ext import db
from wtforms import Form, BooleanField, TextField, PasswordField, validators, ValidationError, IntegerField, SelectField, TextAreaField, FileField


class User(db.Model):
    first_name = db.StringProperty(default="")
    last_name = db.StringProperty(default="")
    address = db.StringProperty(default="")
    postal_code = db.StringProperty(default="")
    contact_num = db.StringProperty(default="")
    contact_num_hide = db.BooleanProperty(default=False)
    institute = db.StringProperty(default="")
    faculty = db.StringProperty(default="")
    course = db.StringProperty(default="")
    rating = db.IntegerProperty(default=0)
    profile_pic = db.BlobProperty()
    prof_complete = db.BooleanProperty(default=False)
    last_active = db.DateTimeProperty(default=datetime.datetime.now())


class UserInfoForm(Form):
    first_name = TextField('First Name:', [validators.required()])
    last_name = TextField('Last Name:', [validators.required()])
    address = TextAreaField('Address:', [validators.optional()])
    postal_code = IntegerField('Postal Code:', [validators.optional()])
    contact_num = IntegerField('Contact Number:', [validators.required()])
    contact_num_hide = SelectField('Contact Visibility:', choices=[('n', 'Viewable by other users'), ('y', 'Hidden from other users')])
    profile_pic = FileField('Upload Profile Picture:')

    def validate_postal_code(form, field):
        if isinstance(field.data, int):
            if field.data < 0:
                raise ValidationError('Enter a valid postal code')

    def validate_hp_num(form, field):
        if isinstance(field.data, int):
            if field.data < 0:
                raise ValidationError('Enter a valid number')


class InstituteInfoForm(Form):
    institute = TextField('Institute:', [validators.required()])
    faculty = TextField('Faculty:', [validators.required()])
    course = TextField('Course:', [validators.required()])


class Book(db.Model):
    module_code = db.StringProperty()
    title = db.StringProperty()
    author = db.StringProperty()
    publisher = db.StringProperty()
    edition = db.IntegerProperty()
    condition = db.IntegerProperty()
    comment = db.StringProperty()
    cost = db.IntegerProperty()


class BookForm(Form):
    module_code = TextField('Module Code', [validators.Length(min=-1, max=10)])
    title = TextField('Title', [validators.Length(min=-1, max=20)])
    author = TextField('Author', [validators.length(min=-1, max=20)])
    publisher = TextField('Publisher', [validators.length(min=-1, max=20)])
    edition = IntegerField('Edition', [validators.number_range(min=1, max=None)])
    cost = IntegerField('Cost', [validators.number_range(min=1, max=None)])
    condition_highlights = BooleanField()
    condition_stains = BooleanField()
    condition_writings = BooleanField()
    condition_dog_eared = BooleanField()
    condition_torn = BooleanField()
    condition_wrapped = BooleanField()
    condition_not_used_once = BooleanField()
    comment = TextAreaField('Comments')