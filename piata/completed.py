import webapp2
import jinja2
import os
import models
import time

from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class Display(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if not currUser.required_complete:
            self.redirect('/profile/edit')

        template_values = {
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url)}

        template = jinja_environment.get_template('completed.html')
        self.response.out.write(template.render(template_values))


app = webapp2.WSGIApplication([('/completed', Display)],
                              debug=True)