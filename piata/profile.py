import webapp2
import jinja2
import os
import models

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api.images import BadImageError, LargeImageError, NotImageError

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class ProfileEdit(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        initial = False
        if not currUser.required_complete:
            initial = True
        template_values = {
            'initial': initial,
            'currUser': currUser,
            'email': user.email(),
            'ratingScale': currUser.rating/50,
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
            currUser.address_hide = True if self.request.get('address_hide').rstrip() == 'True' else False
            currUser.institute = self.request.get('institute').rstrip()
            currUser.faculty = self.request.get('faculty').rstrip()
            currUser.course = self.request.get('course').rstrip()
            trigger = False
            if self.request.get('profile_pic') != "":
                try:
                    currUser.profile_pic = db.Blob(images.resize(self.request.get('profile_pic'), width=200))
                except LargeImageError:
                    trigger = True
                    msg = "Upload a smaller image"
                except (BadImageError, NotImageError):
                    trigger = True
                    msg = "Upload a proper image"
            currUser.required_complete = True
            currUser.put()
            if currUser.address != "" and currUser.postal_code != "" and currUser.profile_pic is not None:
                currUser.prof_complete = True
                currUser.rating = 125
            currUser.put()
            if not trigger:
                self.redirect('/profile')
            else:
                template_values = {
                    'image_error': msg,
                    'currUser': currUser,
                    'email': user.email(),
                    'userform': user_form,
                    'insform': ins_form,
                    'ratingScale': currUser.rating/50,
                    'logout': users.create_logout_url(self.request.host_url)}
                template = jinja_environment.get_template('edit_profile.html')
                self.response.out.write(template.render(template_values))
        else:
            ins_form.validate()
            template_values = {
                'currUser': currUser,
                'email': user.email(),
                'userform': user_form,
                'insform': ins_form,
                'ratingScale': currUser.rating/50,
                'logout': users.create_logout_url(self.request.host_url)}
            template = jinja_environment.get_template('edit_profile.html')
            self.response.out.write(template.render(template_values))


class ViewProfile(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if not currUser.required_complete:
            self.redirect('/profile/edit')
        template_values = {
            'currUser': currUser,
            'ownerEmail': user.email(),
            'ratingScale': currUser.rating/50,
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url)}
        template = jinja_environment.get_template('profile.html')
        self.response.out.write(template.render(template_values))


class ServeImage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if currUser.profile_pic:
            self.response.headers['Content-Type'] = 'image/zxc'
            self.response.out.write(currUser.profile_pic)


class DisplayUser(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if not currUser.required_complete:
            self.redirect('/profile/edit')
        userReq = db.get(db.Key.from_path('User', self.request.url.split('/')[-1]))
        template_values = {
            'currUser': userReq,
            'ownerEmail': user.email(),
            'email': userReq.key().name(),
            'ratingScale': userReq.rating/50,
            'logout': users.create_logout_url(self.request.host_url)}
        template = jinja_environment.get_template('profile.html')
        self.response.out.write(template.render(template_values))


class RateUp(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if not currUser.required_complete:
            self.redirect('/profile/edit')
        userReq = db.get(self.request.url.split('/')[-2])
        self.response.out.write(userReq)
        userReq.rating += 1
        userReq.put()
        self.redirect('/profile/user/' + userReq.key().name())


class RateDown(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if not currUser.required_complete:
            self.redirect('/profile/edit')
        userReq = db.get(self.request.url.split('/')[-2])
        userReq.rating -= 1
        userReq.put()
        self.redirect('/profile/user/' + userReq.key().name())

app = webapp2.WSGIApplication([('/profile', ViewProfile),
                               ('/profile/update', ProfileUpdate),
                               ('/profile/edit', ProfileEdit),
                               ('/profile/image',ServeImage),
                               ('/profile/user/.*?', DisplayUser),
                               ('/profile/.*/up', RateUp),
                               ('/profile/.*/down', RateDown)],
                              debug=True)