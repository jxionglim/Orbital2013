import webapp2
import jinja2
import os
import models

from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class ProcessLogin(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            currUser = db.get(db.Key.from_path('User', users.get_current_user().email()))
            if currUser:
                profile_completed = currUser.prof_complete
                if currUser.first_name != "" and currUser.last_name != "" and currUser.institute != "" and currUser.faculty != "" and currUser.course != "" and currUser.hp_num != "":
                    template_values = {
                        'reminder': profile_completed,
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
        template_values = {
            'reminder': 'yay',
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url),
            }
        template = jinja_environment.get_template('main.html')
        self.response.out.write(template.render(template_values))


class BuyPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
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
