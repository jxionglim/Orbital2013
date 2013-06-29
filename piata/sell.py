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
                'bookid': bookid,
                'logout': users.create_logout_url(self.request.host_url),
                }
        else:
            sellform = models.SellForm(book_pic=None)
            template_values = {
                'email': user.email(),
                'sell_form': sellform,
                'logout': users.create_logout_url(self.request.host_url),
                }
        if not currUser.required_complete:
            self.redirect('/profile/edit')

        template = jinja_environment.get_template('sell.html')
        self.response.out.write(template.render(template_values))


class Submit(webapp2.RequestHandler):
    def get(self):
        self.redirect('/sell')

    def post(self):
        user = users.get_current_user()
        post = models.Post()
        module = models.Module()
        book = models.Book()
        sellform = models.SellForm(self.request.POST)

        if self.request.method == 'POST' and sellform.validate():
            asda = self.request.get('book_id').rstrip()
            self.response.out.write(asda+'111')
            """module.module_code = self.request.get('module_code').rstrip()
            module.put()

            book.title = self.request.get('title').rstrip()
            book.author = self.request.get('author').rstrip()
            book.publisher = self.request.get('publisher').rstrip()
            book.edition = int(self.request.get('edition').rstrip())
            book.module = module
            book.put()

            post.module = module
            post.book = book
            post.user = db.get(db.Key.from_path('User', user.email()))
            post.cost = int(self.request.get('cost').rstrip())
            post.comment = self.request.get('comment').rstrip()

            if self.request.get('condition_stains').rstrip() is not '':
                post.condition.append(self.request.get('condition_stains').rstrip())
            if self.request.get('condition_writings').rstrip() is not '':
                post.condition.append(self.request.get('condition_writings').rstrip())
            if self.request.get('condition_highlights').rstrip() is not '':
                post.condition.append(self.request.get('condition_highlights').rstrip())
            if self.request.get('condition_dog_eared').rstrip() is not '':
                post.condition.append(self.request.get('condition_dog_eared').rstrip())
            if self.request.get('condition_torn').rstrip() is not '':
                post.condition.append(self.request.get('condition_torn').rstrip())
            if self.request.get('condition_wrapped').rstrip() is not '':
                post.condition.append(self.request.get('condition_wrapped').rstrip())
            if self.request.get('condition_not_used_once').rstrip() is not '':
                post.condition.append(self.request.get('condition_not_used_once').rstrip())

            trigger = False
            if self.request.get('book_pic') != "":
                try:
                    post.book_pic = db.Blob(images.resize(self.request.get('book_pic'), width=200))
                except LargeImageError:
                    trigger = True
                    msg = "Upload a smaller image"
                except (BadImageError, NotImageError):
                    trigger = True
                    msg = "Upload a proper image"

            post.put()

            if not trigger:
                pass
                #time.sleep(0.5)
                #self.redirect('/sell/currSale')
            else:
                template_values = {
                    'image_error': msg,
                    'email': user.email(),
                    'sell_form': sellform,
                    'logout': users.create_logout_url(self.request.host_url),
                }
                #template = jinja_environment.get_template('sell.html')
                #self.response.out.write(template.render(template_values))
        else:
            template_values = {
                'email': user.email(),
                'sell_form': sellform,
                'logout': users.create_logout_url(self.request.host_url),
            }

            template = jinja_environment.get_template('sell.html')
            self.response.out.write(template.render(template_values))"""


class DisplaySell(webapp2.RedirectHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))

        posts = models.Post.all().filter('user', currUser)

        currSales = {}

        for post in posts:
            if post.module.module_code.upper() in currSales:
                currSales[post.module.module_code.upper()].append(post)
            else:
                currSales[post.module.module_code.upper()] = [post]

        template_values = {
            'currUser': currUser,
            'currSales': currSales,
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url)}

        template = jinja_environment.get_template('currSale.html')
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
                               ('/sell/currSale', DisplaySell),
                               ('/sell/image/.*?', ServeImage),
                               ('/sell/edit/.*?', SellPage)],
                              debug=True)