import webapp2
import jinja2
import os
import models
import datetime

from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class ProcessLogin(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            currUser = db.get(db.Key.from_path('User', user.email()))
            if currUser:
                currUser.last_active = datetime.datetime.now()
                if currUser.required_complete:
                    template_values = {
                        'reminder': currUser.prof_complete,
                        'searchform': models.SearchForm(),
                        'email': user.email(),
                        'logout': users.create_logout_url(self.request.host_url),
                        }
                    template = jinja_environment.get_template('main.html')
                    self.response.out.write(template.render(template_values))
                else:
                    self.redirect('/profile/edit')
            else:
                newUser = models.User(key_name=user.email())
                newUser.put()
                self.redirect('/profile/edit')
        else:
            self.redirect(self.request.host_url)


class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if not currUser.required_complete:
            self.redirect('/profile/edit')

        template_values = {
            'searchform': models.SearchForm(),
            'search': False,
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url),
            }
        template = jinja_environment.get_template('main.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if not currUser.required_complete:
            self.redirect('/profile/edit')

        search_form = models.SearchForm(self.request.POST)
        if self.request.method == 'POST' and search_form.validate():
            search_cat = self.request.get('search_cat').rstrip()
            search_field = self.request.get('search_field').rstrip()

            tempResult = []
            results = []
            if search_cat == 'module_code':
                moduleList = models.Module.all()
                for module in moduleList:
                    if search_field.upper() in module.module_code:
                        tempResult.append(module)
                for records in tempResult:
                    allRecords = models.Post.all().filter('module', records)
                    for entry in allRecords:
                        results.append(entry)
            else:
                bookList = models.Book.all()
                for book in bookList:
                    if search_field.upper() in getattr(book, search_cat):
                        tempResult.append(book)
                for records in tempResult:
                    allRecords = models.Post.all().filter('book', records)
                    for entry in allRecords:
                        results.append(entry)

            template_values = {
                'searchform': search_form,
                'searchResult': results,
                'search': True,
                'email': user.email(),
                'logout': users.create_logout_url(self.request.host_url),
                }
            template = jinja_environment.get_template('main.html')
            self.response.out.write(template.render(template_values))
        else:
            template_values = {
                'searchform': search_form,
                'search': False,
                'email': user.email(),
                'logout': users.create_logout_url(self.request.host_url),
                }
            template = jinja_environment.get_template('main.html')
            self.response.out.write(template.render(template_values))


class BuyPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if not currUser.required_complete:
            self.redirect('/profile/edit')
        template_values = {
            'reminder': 'yay',
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url),
            }
        template = jinja_environment.get_template('buy.html')
        self.response.out.write(template.render(template_values))


class AdvanceSearchPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if not currUser.required_complete:
            self.redirect('/profile/edit')
        template_values = {
            'reminder': 'yay',
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url),
            }
        template = jinja_environment.get_template('adv_search.html')
        self.response.out.write(template.render(template_values))


class AboutPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if not currUser.required_complete:
            self.redirect('/profile/edit')
        template_values = {
            'reminder': 'yay',
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url),
            }
        template = jinja_environment.get_template('about.html')
        self.response.out.write(template.render(template_values))


class ContactPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if not currUser.required_complete:
            self.redirect('/profile/edit')
        template_values = {
            'reminder': 'yay',
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url),
            }
        template = jinja_environment.get_template('contact.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/login', ProcessLogin),
                               ('/main', MainPage),
                               ('/buy', BuyPage),
                               ('/adv_search', AdvanceSearchPage),
                               ('/about', AboutPage),
                               ('/contact', ContactPage)],
                              debug=True)
