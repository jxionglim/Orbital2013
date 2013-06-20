import webapp2
import jinja2
import os
import models

from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class SellPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template_values = {
            'reminder': 'yay',
            'email': user.email(),
            'book_form': models.BookForm(),
            'logout': users.create_logout_url(self.request.host_url),
            }
        template = jinja_environment.get_template('sell.html')
        self.response.out.write(template.render(template_values))


class Submit(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        myBook = models.Book()
        book_form = models.BookForm(self.request.POST)
        if self.request.method == 'POST' and book_form.validate():
            myBook.module_code = self.request.get('module').rstrip()
            myBook.title = self.request.get('title').rstrip()
            myBook.author = self.request.get('author').rstrip()
            myBook.publisher = self.request.get('publisher').rstrip()
            myBook.edition = int(self.request.get('edition').rstrip())
            myBook.cost = int(self.request.get('cost').rstrip())
            myBook.comment = self.request.get('comments').rstrip()
            conditions = self.request.get('conditions', allow_multiple=True)

            for a in conditions:
                if a == 'not_used_once':
                    condition = 7
                else:
                    condition = 5

            myBook.condition = condition
            myBook.put()
            self.redirect('/sell/submit')

        template_values = {
            'myBook': myBook,
            'email': user.email(),
            'book_form': book_form,
            'logout': users.create_logout_url(self.request.host_url),
        }
        template = jinja_environment.get_template('sell.html')
        self.response.out.write(template.render(template_values))



app = webapp2.WSGIApplication([('/sell', SellPage),
                               ('/sell/submit' , Submit)],
                              debug=True)