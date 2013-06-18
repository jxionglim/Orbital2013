import webapp2
import jinja2
import os
import models

from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class ProfilePage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template_values = {
            'reminder': 'yay',
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url),
            }
        template = jinja_environment.get_template('profile.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/profile', ProfilePage)],
                              debug=True)
