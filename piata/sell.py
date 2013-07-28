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
from google.appengine.api import mail

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class SellPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        url = self.request.url
        if not currUser.required_complete:
            self.redirect('/profile/edit')
        if "edit" in url:
            currPost = models.Post.get_by_id(int(url.split('/')[-1]))
            bookid = int(url.split('/')[-1])

            stains = True if 'Stains' in currPost.condition else False
            highlights = True if 'Highlights' in currPost.condition else False
            writings = True if 'Writings' in currPost.condition else False
            dog_eared = True if 'Dog Eared' in currPost.condition else False
            torn = True if 'Torn' in currPost.condition else False
            wrapped = True if 'Wrapped' in currPost.condition else False
            not_used_once = True if 'Not Used Once' in currPost.condition else False

            sellform = models.SellForm(module_code=currPost.module.module_code.upper(), title=currPost.book.title, author=currPost.book.author, publisher=currPost.book.publisher, edition=currPost.book.edition, cost=currPost.cost, condition_highlights=highlights, condition_stains=stains, condition_writings=writings, condition_dog_eared=dog_eared, condition_torn=torn, condition_wrapped=wrapped, condition_not_used_once=not_used_once, comment=currPost.comment, book_pic=currPost.book_pic)
            template_values = {
                'email': user.email(),
                'sell_form': sellform,
                'currPost': currPost,
                'bookid': bookid,
                'logout': users.create_logout_url(self.request.host_url),
                }
        else:
            sellform = models.SellForm()
            template_values = {
                'email': user.email(),
                'sell_form': sellform,
                'logout': users.create_logout_url(self.request.host_url),
                }
        template = jinja_environment.get_template('sell.html')
        self.response.out.write(template.render(template_values))


class Submit(webapp2.RequestHandler):
    def get(self):
        self.redirect('/sell')

    def post(self):
        user = users.get_current_user()
        if self.request.get('book_id').rstrip() == '':
            currPost = models.Post()
            currModule = models.Module()
            currBook = models.Book()
        else:
            currPost = models.Post.get_by_id(int(self.request.get('book_id').rstrip()))
            currModule = models.Module()
            currBook = models.Book()

        sellform = models.SellForm(self.request.POST)

        if self.request.method == 'POST' and sellform.validate():
            q = db.Query(models.Module)
            q.filter('module_code =', self.request.get('module_code').rstrip().upper())
            result_module = q.get()
            if result_module is None:
                currModule.module_code = self.request.get('module_code').rstrip().upper()
                currModule.put()
            else:
                currModule = result_module

            q1 = db.Query(models.Book)
            q1.filter('title =', self.request.get('title').rstrip().lower()).filter('author', self.request.get('author').rstrip().lower()).filter('publisher', self.request.get('publisher').rstrip().lower()).filter('edition', int(self.request.get('edition').rstrip()))
            result_book = q1.get()

            if result_book is None:
                currBook.title = self.request.get('title').rstrip().lower()
                currBook.author = self.request.get('author').rstrip().lower()
                currBook.publisher = self.request.get('publisher').rstrip().lower()
                currBook.edition = int(self.request.get('edition').rstrip())
                currBook.module = currModule
                currBook.put()
            else:
                currBook = result_book

            currPost.module = currModule
            currPost.book = currBook
            currPost.user = db.get(db.Key.from_path('User', user.email()))
            currPost.cost = int(self.request.get('cost').rstrip())
            currPost.comment = self.request.get('comment').rstrip()

            currPost.condition = []

            if self.request.get('condition_stains').rstrip() is not '' and self.request.get('condition_stains').rstrip() not in currPost.condition:
                currPost.condition.append(self.request.get('condition_stains').rstrip())
            if self.request.get('condition_writings').rstrip() is not '' and self.request.get('condition_writings').rstrip() not in currPost.condition:
                currPost.condition.append(self.request.get('condition_writings').rstrip())
            if self.request.get('condition_highlights').rstrip() is not '' and self.request.get('condition_highlights').rstrip() not in currPost.condition:
                currPost.condition.append(self.request.get('condition_highlights').rstrip())
            if self.request.get('condition_dog_eared').rstrip() is not '' and self.request.get('condition_dog_eared').rstrip() not in currPost.condition:
                currPost.condition.append(self.request.get('condition_dog_eared').rstrip())
            if self.request.get('condition_torn').rstrip() is not '' and self.request.get('condition_torn').rstrip() not in currPost.condition:
                currPost.condition.append(self.request.get('condition_torn').rstrip())
            if self.request.get('condition_wrapped').rstrip() is not '' and self.request.get('condition_wrapped').rstrip() not in currPost.condition:
                currPost.condition.append(self.request.get('condition_wrapped').rstrip())
            if self.request.get('condition_not_used_once').rstrip() is not '' and self.request.get('condition_not_used_once').rstrip() not in currPost.condition:
                currPost.condition.append(self.request.get('condition_not_used_once').rstrip())

            trigger = False
            if self.request.get('book_pic') != "":
                try:
                    currPost.book_pic = db.Blob(images.resize(self.request.get('book_pic'), width=200))
                except LargeImageError:
                    trigger = True
                    msg = "Upload a smaller image"
                except (BadImageError, NotImageError):
                    trigger = True
                    msg = "Upload a proper image"

            currPost.put()
            checkStatus(currPost)

            if not trigger:
                time.sleep(0.5)
                self.redirect('/current')
            else:
                template_values = {
                    'image_error': msg,
                    'email': user.email(),
                    'sell_form': sellform,
                    'logout': users.create_logout_url(self.request.host_url),
                }
                template = jinja_environment.get_template('sell.html')
                self.response.out.write(template.render(template_values))
        else:
            template_values = {
                'bookpic': currPost.book_pic,
                'email': user.email(),
                'sell_form': sellform,
                'logout': users.create_logout_url(self.request.host_url),
            }

            template = jinja_environment.get_template('sell.html')
            self.response.out.write(template.render(template_values))


def checkStatus(currPost):
    q = db.Query(models.Request)
    q.order('request_date')

    results = q.get()

    if results is not None:
        currRequest = results
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        cost = map(int, re.findall(r'\d+', currRequest.cost_range))

        if cost.__len__() == 1:
            cost_lower = cost.__getitem__(0)
            cost_upper = cost.__getitem__(0)
        else:
            cost_lower = cost.__getitem__(0)
            cost_upper = cost.__getitem__(1)

        if currRequest.module.module_code == currPost.module.module_code and currRequest.book.title == currPost.book.title and currRequest.book.author == currPost.book.author and currRequest.book.publisher == currPost.book.publisher and currRequest.book.edition == currPost.book.edition and cost_lower <= currPost.cost <= cost_upper and currPost.status != "Matched" and currRequest.user.key() != currUser.key():
            currPost.status = "Matched"
            currPost.matched_request = currRequest
            currPost.put()
            currRequest.status = "Matched"
            if currPost.key() not in currRequest.matched_posts:
                currRequest.matched_posts.append(currPost.key())
            currRequest.put()
            url = "http://piata-sg.appspot.com/matched/" + str(currRequest.key().id())
            message = mail.EmailMessage()
            message.sender = "teamlupus.13@gmail.com"
            message.to = str(currRequest.user.key().name())
            message.subject = "A match has been found for " + str(currRequest.book.title.title())
            message.body = """
A match has been found for the book that you have requested.

Please click the following link below to access it.

%s

With Regards,

Team Lupus
                    """ % url

            message.send()
        else:
            currPost.status = "Pending"
            if currPost.matched_request != '':
                currPost.matched_request = None
            currPost.put()
            if currPost.key() in currRequest.matched_posts:
                currRequest.matched_posts.remove(currPost.key())
                if currRequest.matched_posts.__len__() == 0:
                    currRequest.status = "Pending"
            currRequest.put()
    else:
        currPost.status = "Pending"
        currPost.put()


class ServeImage(webapp2.RequestHandler):
    def get(self):
        url = self.request.url
        currPost = models.Post.get_by_id(int(url.split('/')[-1]))
        if currPost:
            if currPost.book_pic:
                self.response.headers['Content-Type'] = 'image/zxc'
                self.response.out.write(currPost.book_pic)


app = webapp2.WSGIApplication([('/sell', SellPage),
                               ('/sell/submit' , Submit),
                               ('/sell/image/.*?', ServeImage),
                               ('/sell/edit/.*?', SellPage)],
                              debug=True)