import webapp2
import jinja2
import os
import models
import time

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api.images import BadImageError, LargeImageError, NotImageError

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class BuyPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        buyform = models.BuyForm()
        template_values = {
            'email': user.email(),
            'buy_form': buyform,
            'logout': users.create_logout_url(self.request.host_url),
        }

        template = jinja_environment.get_template('buy.html')
        self.response.out.write(template.render(template_values))


class Submit(webapp2.RequestHandler):
    def get(self):
        self.redirect('/buy')

    def post(self):
        user = users.get_current_user()

        currRequest = models.Request()
        currModule = models.Module()
        currBook = models.Book()

        buyform = models.BuyForm(self.request.POST)

        if self.request.method == 'POST' and buyform.validate():
            q = db.Query(models.Module)
            q.filter('module_code =', self.request.get('module_code').rstrip().upper())
            result_module = q.get()
            if result_module is None:
                currModule.module_code = self.request.get('module_code').rstrip().upper()
                currModule.put()
            else:
                currModule = result_module

            q1 = db.Query(models.Book)
            q1.filter('title =', self.request.get('title').rstrip().lower())
            result_book = q1.get()

            status = False
            if result_book is not None:
                if result_book.author == self.request.get('author').rstrip().lower() and result_book.publisher == self.request.get('publisher').rstrip().lower() and result_book.edition == int(self.request.get('edition').rstrip()):
                    currBook = result_book
                    status = True

            if status is False:
                currBook.title = self.request.get('title').rstrip().lower()
                currBook.author = self.request.get('author').rstrip().lower()
                currBook.publisher = self.request.get('publisher').rstrip().lower()
                currBook.edition = int(self.request.get('edition').rstrip())
                currBook.module = currModule
                currBook.put()

            currRequest.module = currModule
            currRequest.book = currBook
            currRequest.user = db.get(db.Key.from_path('User', user.email()))
            currRequest.cost_range = self.request.get('cost_lower').rstrip() + "-" + self.request.get('cost_upper').rstrip()

            currRequest.condition = []

            if self.request.get('condition_stains').rstrip() is not '' and self.request.get('condition_stains').rstrip() not in currRequest.condition:
                currRequest.condition.append(self.request.get('condition_stains').rstrip())
            if self.request.get('condition_writings').rstrip() is not '' and self.request.get('condition_writings').rstrip() not in currRequest.condition:
                currRequest.condition.append(self.request.get('condition_writings').rstrip())
            if self.request.get('condition_highlights').rstrip() is not '' and self.request.get('condition_highlights').rstrip() not in currRequest.condition:
                currRequest.condition.append(self.request.get('condition_highlights').rstrip())
            if self.request.get('condition_dog_eared').rstrip() is not '' and self.request.get('condition_dog_eared').rstrip() not in currRequest.condition:
                currRequest.condition.append(self.request.get('condition_dog_eared').rstrip())
            if self.request.get('condition_torn').rstrip() is not '' and self.request.get('condition_torn').rstrip() not in currRequest.condition:
                currRequest.condition.append(self.request.get('condition_torn').rstrip())
            if self.request.get('condition_wrapped').rstrip() is not '' and self.request.get('condition_wrapped').rstrip() not in currRequest.condition:
                currRequest.condition.append(self.request.get('condition_wrapped').rstrip())
            if self.request.get('condition_not_used_once').rstrip() is not '' and self.request.get('condition_not_used_once').rstrip() not in currRequest.condition:
                currRequest.condition.append(self.request.get('condition_not_used_once').rstrip())

            currRequest.put()

            self.response.out.write(currRequest.cost_range)

        else:
            template_values = {
                'email': user.email(),
                'buy_form': buyform,
                'logout': users.create_logout_url(self.request.host_url),
            }

            template = jinja_environment.get_template('buy.html')
            self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/buy', BuyPage),
                               ('/buy/submit', Submit)],
                              debug=True)