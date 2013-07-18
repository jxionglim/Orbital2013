import webapp2
import jinja2
import os
import models
import time
import re

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api.images import BadImageError, LargeImageError, NotImageError

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class BuyPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        url = self.request.url
        if not currUser.required_complete:
            self.redirect('/profile/edit')

        if "edit" in url:
            currRequest = models.Request.get_by_id(int(url.split('/')[-1]))
            bookid = int(url.split('/')[-1])

            stains = True if 'Stains' in currRequest.condition else False
            highlights = True if 'Highlights' in currRequest.condition else False
            writings = True if 'Writings' in currRequest.condition else False
            dog_eared = True if 'Dog Eared' in currRequest.condition else False
            torn = True if 'Torn' in currRequest.condition else False
            wrapped = True if 'Wrapped' in currRequest.condition else False
            not_used_once = True if 'Not Used Once' in currRequest.condition else False

            cost = map(int, re.findall(r'\d+', currRequest.cost_range))

            if cost.__len__() == 1:
                cost_lower = cost.__getitem__(0)
                cost_upper = cost.__getitem__(0)
            else:
                cost_lower = cost.__getitem__(0)
                cost_upper = cost.__getitem__(1)

            buyform = models.BuyForm(module_code=currRequest.module.module_code.upper(), title=currRequest.book.title, author=currRequest.book.author, publisher=currRequest.book.publisher, edition=currRequest.book.edition, cost_lower=cost_lower, cost_upper=cost_upper, condition_highlights=highlights, condition_stains=stains, condition_writings=writings, condition_dog_eared=dog_eared, condition_torn=torn, condition_wrapped=wrapped, condition_not_used_once=not_used_once)
            template_values = {
                'email': user.email(),
                'buy_form': buyform,
                'currRequest': currRequest,
                'bookid': bookid,
                'logout': users.create_logout_url(self.request.host_url),
                }
        else:
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

        if self.request.get('book_id').rstrip() == '':
            currRequest = models.Request()
            currModule = models.Module()
            currBook = models.Book()
        else:
            currRequest = models.Request.get_by_id(int(self.request.get('book_id').rstrip()))
            currModule = currRequest.module
            currBook = currRequest.book

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
            if int(self.request.get('cost_lower').rstrip()) == int(self.request.get('cost_upper').rstrip()):
                currRequest.cost_range = "$" + self.request.get('cost_lower').rstrip()
            elif int(self.request.get('cost_lower').rstrip()) > int(self.request.get('cost_upper').rstrip()):
                currRequest.cost_range = "$" + self.request.get('cost_upper').rstrip() + " - $" + self.request.get('cost_lower').rstrip()
            else:
                currRequest.cost_range = "$" + self.request.get('cost_lower').rstrip() + " - $" + self.request.get('cost_upper').rstrip()

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

            time.sleep(0.5)
            self.redirect('/current')

        else:
            template_values = {
                'email': user.email(),
                'buy_form': buyform,
                'logout': users.create_logout_url(self.request.host_url),
            }

            template = jinja_environment.get_template('buy.html')
            self.response.out.write(template.render(template_values))


app = webapp2.WSGIApplication([('/buy', BuyPage),
                               ('/buy/submit', Submit),
                               ('/buy/edit/.*?', BuyPage)],
                              debug=True)