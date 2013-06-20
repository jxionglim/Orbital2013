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
        module = self.request.get('module').rstrip()
        title = self.request.get('title').rstrip()
        author = self.request.get('author').rstrip()
        publisher = self.request.get('publisher').rstrip()
        edition = self.request.get('edition').rstrip()
        cost = self.request.get('cost').rstrip()
        comments = self.request.get('comments').rstrip()
        zxc = self.request.get('conditions', allow_multiple=True)

        for a in zxc:
            if a == 'not_used_once':
                condition = 7
            else:
                condition = 3

        template_values = {
            'module': module,
            'title': title,
            'author': author,
            'publisher': publisher,
            'edition': edition,
            'cost': cost,
            'comments': comments,
            'condition': condition,
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url),
            'asd': zxc,
            }
        template = jinja_environment.get_template('submit.html')
        self.response.out.write(template.render(template_values))



app = webapp2.WSGIApplication([('/sell', SellPage),
                               ('/sell/submit' , Submit)],
                              debug=True)