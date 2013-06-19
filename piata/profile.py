import webapp2
import jinja2
import os
import models

from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class ProfileEdit(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        template_values = {
            'currUser': currUser,
            'email': user.email(),
            'user_form': models.UserForm(),
            'logout': users.create_logout_url(self.request.host_url),
            }
        template = jinja_environment.get_template('edit_profile.html')
        self.response.out.write(template.render(template_values))


class ProfileUpdate(webapp2.RequestHandler):
    def post(self):
        myForm = models.UserForm(self.request.params)
        if myForm.validate():
            self.response.out.write('<html>valid</html>')
        else:
            self.response.out.write('<html>invalid</html>')
        """user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        currUser.first_name = self.request.get('first_name').rstrip()
        currUser.last_name = self.request.get('last_name').rstrip()
        currUser.address = self.request.get('address').rstrip()
        currUser.postal_code = self.request.get('postal_code').rstrip()
        currUser.institute = self.request.get('institute').rstrip()
        currUser.faculty = self.request.get('faculty').rstrip()
        currUser.course = self.request.get('course').rstrip()
        currUser.hp_num = self.request.get('hp_num').rstrip()
        currUser.hp_num_hide = True if self.request.get('hp_num_hide').rstrip() != "" else False
        currUser.home_num = self.request.get('home_num').rstrip()
        currUser.home_num_hide = True if self.request.get('home_num_hide').rstrip() != "" else False
        currUser.put()
        self.redirect('/profile')"""


class ViewProfile(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        template_values = {
            'currUser': currUser,
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url),
            }
        template = jinja_environment.get_template('profile.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/profile', ViewProfile),
                               ('/profile/update', ProfileUpdate),
                               ('/profile/edit', ProfileEdit)],
                              debug=True)
