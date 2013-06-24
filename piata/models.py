import datetime
from google.appengine.ext import db
from wtforms import Form, BooleanField, TextField, validators, ValidationError, IntegerField, SelectField, TextAreaField, FileField, HiddenField


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
    required_complete = db.BooleanProperty(default=False)
    last_active = db.DateTimeProperty(default=datetime.datetime.now())


class UserInfoForm(Form):
    first_name = TextField('First Name:', [validators.required()])
    last_name = TextField('Last Name:', [validators.required()])
    address = TextAreaField('Address:', [validators.optional()])
    postal_code = IntegerField('Postal Code:', [validators.optional()])
    contact_num = IntegerField('Contact Number:', [validators.required()])
    contact_num_hide = SelectField('Contact Visibility:', choices=[('n', 'Viewable by other users'),
                                                                   ('y', 'Hidden from other users')])
    profile_pic = FileField('Upload Profile Picture:', [validators.optional()])

    def validate_postal_code(form, field):
        if isinstance(field.data, int):
            if field.data < 0:
                raise ValidationError('Enter a valid postal code')

    def validate_contact_num(form, field):
        if isinstance(field.data, int):
            if field.data < 0:
                raise ValidationError('Enter a valid number')


class InstituteInfoForm(Form):
    institute = TextField('Institute:', [validators.required()])
    faculty = TextField('Faculty:', [validators.required()])
    course = TextField('Course:', [validators.required()])


class SearchForm(Form):
    search_type = SelectField('Search Category', choices=[('module_code', 'Module Code'),
                                                          ('title', 'Title'),
                                                          ('author', 'Author'),
                                                          ('publisher', 'Publisher')])
    search_field = TextField('Keyword', [validators.optional()])


class Book(db.Model):
    module_code = db.StringProperty(default="")
    title = db.StringProperty(default="")
    author = db.StringProperty(default="")
    publisher = db.StringProperty(default="")
    edition = db.IntegerProperty(default=0)
    condition = db.ListProperty(str)
    comment = db.StringProperty(multiline='True')
    cost = db.IntegerProperty(default=0)
    book_pic = db.BlobProperty()
    user = db.ReferenceProperty(User, collection_name="books_onSale")


class BookForm(Form):
    module_code = TextField('Module Code', [validators.Required()])
    title = TextField('Title', [validators.Required()])
    author = TextField('Author', [validators.Required()])
    publisher = TextField('Publisher', [validators.Required()])
    edition = IntegerField('Edition', [validators.number_range(min=1, max=None)])
    cost = IntegerField('Cost', [validators.number_range(min=1, max=None)])
    condition_highlights = BooleanField([validators.optional()])
    condition_stains = BooleanField([validators.optional()])
    condition_writings = BooleanField([validators.optional()])
    condition_dog_eared = BooleanField([validators.optional()])
    condition_torn = BooleanField([validators.optional()])
    condition_wrapped = BooleanField([validators.optional()])
    condition_not_used_once = BooleanField([validators.optional()])
    comment = TextAreaField("Comment", [validators.optional()])
    book_pic = HiddenField(FileField)