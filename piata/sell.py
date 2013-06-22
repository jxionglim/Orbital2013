import webapp2
import jinja2
import os
import models

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import images

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class SellPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if not currUser.required_complete:
            self.redirect('/profile/edit')
        template_values = {
            'email': user.email(),
            'book_form': models.BookForm(),
            'logout': users.create_logout_url(self.request.host_url),
        }
        template = jinja_environment.get_template('sell.html')
        self.response.out.write(template.render(template_values))


class Submit(webapp2.RequestHandler):
    def get(self):
        self.redirect('/sell')

    def post(self):
        user = users.get_current_user()
        myBook = models.Book()
        book_form = models.BookForm(self.request.POST)
        if self.request.method == 'POST' and book_form.validate():
            myBook.module_code = self.request.get('module_code').rstrip()
            myBook.title = self.request.get('title').rstrip()
            myBook.author = self.request.get('author').rstrip()
            myBook.publisher = self.request.get('publisher').rstrip()
            myBook.edition = int(self.request.get('edition').rstrip())
            myBook.cost = int(self.request.get('cost').rstrip())
            myBook.comment = self.request.get('comments').rstrip()
            myBook.condition = self.request.get('conditions', allow_multiple=True)
            myBook.book_pic = db.Blob(images.resize(self.request.get('book_pic'), width=200))
            myBook.user = db.get(db.Key.from_path('User', user.email()))
            myBook.put()
            self.redirect('/main')

        template_values = {
            'myBook': myBook,
            'email': user.email(),
            'book_form': book_form,
            'logout': users.create_logout_url(self.request.host_url),
        }
        template = jinja_environment.get_template('sell.html')
        self.response.out.write(template.render(template_values))


class DisplaySell(webapp2.RedirectHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))

        template_values = {
            'currUser': currUser,
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url)}

        template = jinja_environment.get_template('currSale.html')
        self.response.out.write(template.render(template_values))


app = webapp2.WSGIApplication([('/sell', SellPage),
                               ('/sell/submit' , Submit),
                               ("/sell/currSale", DisplaySell)],
                              debug=True)