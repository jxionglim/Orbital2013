import webapp2
import jinja2
import os
import models
import time

from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class DisplaySell(webapp2.RedirectHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if not currUser.required_complete:
            self.redirect('/profile/edit')

        posts = models.Post.all().filter('user', currUser)

        requests = models.Request.all().filter('user', currUser)

        currSales = {}
        currRequests = {}

        for post in posts:
            if post.module.module_code.upper() in currSales:
                currSales[post.module.module_code.upper()].append(post)
            else:
                currSales[post.module.module_code.upper()] = [post]

        for request in requests:
            if request.module.module_code.upper() in currRequests:
                currRequests[request.module.module_code.upper()].append(request)
            else:
                currRequests[request.module.module_code.upper()] = [request]

        template_values = {
            'currUser': currUser,
            'currSales': currSales,
            'currRequests': currRequests,
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url)}

        template = jinja_environment.get_template('currSale.html')
        self.response.out.write(template.render(template_values))


class Delete(webapp2.RedirectHandler):
    def get(self):
        user = users.get_current_user()
        url = self.request.url
        currPost = models.Post.get_by_id(int(url.split('/')[-1]))
        if currPost:
            currPost.delete()

        time.sleep(0.5)
        self.redirect('/current')


app = webapp2.WSGIApplication([('/current', DisplaySell),
                               ('/current/delete/.*?', Delete)],
                              debug=True)