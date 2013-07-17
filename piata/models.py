import datetime
from google.appengine.ext import db
from wtforms import Form, BooleanField, TextField, validators, ValidationError, IntegerField, SelectField, TextAreaField, FileField, HiddenField
import re


class User(db.Model):
    first_name = db.StringProperty(default="")
    last_name = db.StringProperty(default="")
    address = db.StringProperty(default="", multiline='True')
    postal_code = db.StringProperty(default="")
    contact_num = db.StringProperty(default="")
    address_hide = db.BooleanProperty(default=False)
    institute = db.StringProperty(default="")
    faculty = db.StringProperty(default="")
    course = db.StringProperty(default="")
    rating = db.IntegerProperty(default=0)
    profile_pic = db.BlobProperty()
    prof_complete = db.BooleanProperty(default=False)
    required_complete = db.BooleanProperty(default=False)
    last_active = db.DateTimeProperty(default=datetime.datetime.now())


class Module(db.Model):
    module_code = db.StringProperty(default="")


class Book(db.Model):
    title = db.StringProperty(default="")
    author = db.StringProperty(default="")
    publisher = db.StringProperty(default="")
    edition = db.IntegerProperty(default=0)
    module = db.ReferenceProperty(Module, collection_name="booklist")


class Post(db.Model):
    module = db.ReferenceProperty(Module)
    book = db.ReferenceProperty(Book)
    user = db.ReferenceProperty(User, collection_name="books_onSale")
    condition = db.ListProperty(str)
    comment = db.StringProperty(multiline='True')
    cost = db.IntegerProperty(default=0)
    book_pic = db.BlobProperty()


class Request(db.Model):
    module = db.ReferenceProperty(Module)
    book = db.ReferenceProperty(Book)
    user = db.ReferenceProperty(User, collection_name="books_onRequest")
    cost_range = db.StringProperty(default="")
    condition = db.ListProperty(str)


class SaleRecord(db.Model):
    book = db.ReferenceProperty(Book)
    cost = db.IntegerProperty(default=0)
    sold_date = db.DateTimeProperty(default=datetime.datetime.now())


class UserInfoForm(Form):
    first_name = TextField('First Name', [validators.required()])
    last_name = TextField('Last Name', [validators.required()])
    address = TextAreaField('Address', [validators.optional()])
    postal_code = IntegerField('Postal Code', [validators.optional()])
    contact_num = IntegerField('Contact Number', [validators.required(message="Enter a 9 digit number")])
    address_hide = SelectField('Address Visibility', choices=[('False', 'Viewable by other users'),
                                                              ('True', 'Hidden from other users')])
    profile_pic = FileField('Upload Profile Picture:', [validators.optional()])

    def validate_postal_code(form, field):
        if isinstance(field.data, int):
            if not re.match('^\d{6}$', str(field.data)):
                raise ValidationError('Enter a 6 digit postal code')

    def validate_contact_num(form, field):
        if isinstance(field.data, int):
            if not re.match('^(9|8|6)\d{7}$', str(field.data)):
                raise ValidationError('Enter a 9 digit number')


class InstituteInfoForm(Form):
    institute = TextField('Institute', [validators.required()])
    faculty = TextField('Faculty', [validators.required()])
    course = TextField('Course', [validators.required()])


class SearchForm(Form):
    search_cat = SelectField('Search Category', choices=[('module_code', 'Module Code'),
                                                         ('title', 'Title'),
                                                         ('author', 'Author'),
                                                         ('publisher', 'Publisher')])
    search_field = TextField('Keyword', [validators.optional()])


class AdvSearchForm(Form):
    module_code = TextField('Module Code', [validators.optional()])
    module_code_type = SelectField(choices=[('exact', 'Exact'),
                                            ('contains', 'Contains')])
    title = TextField('Title', [validators.optional()])
    title_type = SelectField(choices=[('exact', 'Exact'),
                                      ('contains', 'Contains')])
    author = TextField('Author', [validators.optional()])
    author_type = SelectField(choices=[('exact', 'Exact'),
                                       ('contains', 'Contains')])
    publisher = TextField('Publisher', [validators.optional()])
    publisher_type = SelectField(choices=[('exact', 'Exact'),
                                          ('contains', 'Contains')])
    edition = IntegerField('Edition', [validators.optional(), validators.number_range(min=1, max=None)])
    edition_type = SelectField(choices=[('=', '='),
                                        ('>', '>'),
                                        ('<', '<')])
    cost = IntegerField('Cost', [validators.optional(), validators.number_range(min=1, max=None)])
    cost_type = SelectField(choices=[('=', '='),
                                     ('>', '>'),
                                     ('<', '<')])
    condition_highlights = BooleanField('Highlights', [validators.optional()])
    condition_stains = BooleanField('Stains', [validators.optional()])
    condition_writings = BooleanField('Writings', [validators.optional()])
    condition_dog_eared = BooleanField('Dog Eared', [validators.optional()])
    condition_torn = BooleanField('Torn', [validators.optional()])
    condition_wrapped = BooleanField('Wrapped', [validators.optional()])
    condition_not_used_once = BooleanField('Not Used Once', [validators.optional()])


class SellForm(Form):
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
    book_pic = HiddenField(FileField, [validators.optional()])
    book_id = HiddenField(TextField, [validators.optional()])


class BuyForm(Form):
    module_code = TextField('Module Code', [validators.Required()])
    title = TextField('Title', [validators.Required()])
    author = TextField('Author', [validators.Required()])
    publisher = TextField('Publisher', [validators.Required()])
    edition = IntegerField('Edition', [validators.number_range(min=1, max=None)])
    cost_lower = IntegerField('cost_lower', [validators.number_range(min=1, max=None)])
    cost_upper = IntegerField('cost_upper', [validators.number_range(min=1, max=None)])
    condition_highlights = BooleanField([validators.optional()])
    condition_stains = BooleanField([validators.optional()])
    condition_writings = BooleanField([validators.optional()])
    condition_dog_eared = BooleanField([validators.optional()])
    condition_torn = BooleanField([validators.optional()])
    condition_wrapped = BooleanField([validators.optional()])
    condition_not_used_once = BooleanField([validators.optional()])