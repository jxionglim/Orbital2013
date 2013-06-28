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
            currBook = models.Book.get_by_id(int(url.split('/')[-1]))
            bookid = int(url.split('/')[-1])
            sellform = models.SellForm(obj=currBook)
            template_values = {
                'email': user.email(),
                'sell_form': sellform,
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
        if not currUser.required_complete:
            self.redirect('/profile/edit')

        template = jinja_environment.get_template('sell.html')
        self.response.out.write(template.render(template_values))


class Submit(webapp2.RequestHandler):
    def get(self):
        self.redirect('/sell')

        user = users.get_current_user()

        post = models.Post()
        module = models.Module()
        book = models.Book()

        book.title = "asd"
        book.author = "asd"
        book.publisher = "asd"
        book.edition = 1
        book.put()

        module.book = book
        module.module_code = "qwe"
        module.put()

        post.module = module
        post.book = book
        post.user = db.get(db.Key.from_path('User', user.email()))
        post.cost = 1
        post.comment = "asd"
        post.put()

    def post(self):
        user = users.get_current_user()
        post = models.Post()
        module = models.Module()
        book = models.Book()
        sellform = models.SellForm(self.request.POST)

        '''if self.request.get('condition_stains').rstrip() is not '':
            post.condition.append(self.request.get('condition_stains').rstrip())
        if self.request.get('condition_writings').rstrip() is not '':
            post.condition.append(self.request.get('condition_writings').rstrip())

        self.response.out.write(post.condition)'''
        '''self.response.out.write(self.request.get('condition_stains').rstrip())'''

        '''self.response.out.write(post.module.get())'''
        if self.request.method == 'POST' and sellform.validate():
            module.module_code = self.request.get('module_code').rstrip()
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
                time.sleep(0.5)
                self.redirect('/sell/currSale')
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
                'email': user.email(),
                'sell_form': sellform,
                'logout': users.create_logout_url(self.request.host_url),
            }

            template = jinja_environment.get_template('sell.html')
            self.response.out.write(template.render(template_values))


class DisplaySell(webapp2.RedirectHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))

        modules = models.Module().all()

        post = models.Post.all().filter('user', currUser)

        for test in post:
            asd = test.module.module_code
            qwe = test.book.title

        '''self.response.out.write(asd)
        self.response.out.write(qwe)'''

        template_values = {
            'currUser': currUser,
            'modules': modules,
            'asd': asd,
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url)}

        template = jinja_environment.get_template('currSale.html')
        self.response.out.write(template.render(template_values))


class ServeImage(webapp2.RequestHandler):
    def get(self):
        url = self.request.url
        currBook = models.Book.get_by_id(int(url.split('/')[-1]))
        if currBook:
            if currBook.book_pic:
                self.response.headers['Content-Type'] = 'image/zxc'
                self.response.out.write(currBook.book_pic)


app = webapp2.WSGIApplication([('/sell', SellPage),
                               ('/sell/submit' , Submit),
                               ('/sell/currSale', DisplaySell),
                               ('/sell/image/.*?', ServeImage),
                               ('/sell/edit/.*?', SellPage)],
                              debug=True)