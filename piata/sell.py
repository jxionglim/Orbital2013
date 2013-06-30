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
            currModule = currPost.module
            currBook = currPost.book

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

            if not trigger:
                pass
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