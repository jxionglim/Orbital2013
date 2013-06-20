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
            'userform': models.UserInfoForm(obj=currUser),
            'insform': models.InstituteInfoForm(obj=currUser),
            'logout': users.create_logout_url(self.request.host_url),}
        template = jinja_environment.get_template('edit_profile.html')
        self.response.out.write(template.render(template_values))


class ProfileUpdate(webapp2.RequestHandler):
    def get(self):
        self.redirect('/profile/edit')

    def post(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        user_form = models.UserInfoForm(self.request.POST)
        ins_form = models.InstituteInfoForm(self.request.POST)
        if self.request.method == 'POST' and user_form.validate() and ins_form.validate():
            currUser.first_name = self.request.get('first_name').rstrip()
            currUser.last_name = self.request.get('last_name').rstrip()
            currUser.address = self.request.get('address').rstrip()
            currUser.postal_code = self.request.get('postal_code').rstrip()
            currUser.contact_num = self.request.get('contact_num').rstrip()
            currUser.contact_num_hide = True if self.request.get('contact_num_hide').rstrip() == 'y' else False
            currUser.institute = self.request.get('institute').rstrip()
            currUser.faculty = self.request.get('faculty').rstrip()
            currUser.course = self.request.get('course').rstrip()
            currUser.profile_pic = db.Blob(self.request.get('profile_pic'))
            currUser.put()
            self.redirect('/profile')
        else:
            ins_form.validate()
        template_values = {
            'currUser': currUser,
            'email': user.email(),
            'userform': user_form,
            'insform': ins_form,
            'logout': users.create_logout_url(self.request.host_url)}
        template = jinja_environment.get_template('edit_profile.html')
        self.response.out.write(template.render(template_values))


class ViewProfile(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        template_values = {
            'currUser': currUser,
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url)}
        template = jinja_environment.get_template('profile.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/profile', ViewProfile),
                               ('/profile/update', ProfileUpdate),
                               ('/profile/edit', ProfileEdit)],
                              debug=True)