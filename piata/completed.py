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

        completedPosts = models.Post.all().filter('user', currUser).filter('status', "Completed")
        completedPostsPurchased = models.Post.all().filter('seller', currUser).filter('status', "Completed")
        completedRequests = models.Request.all().filter('user', currUser).filter('status', "Completed")


        completedSales = {}
        completedPurchased = {}
        completedRequestsPurchased = {}

        for post in completedPosts:
            if post.module.module_code.upper() in completedSales:
                completedSales[post.module.module_code.upper()].append(post)
            else:
                completedSales[post.module.module_code.upper()] = [post]

        for post in completedPostsPurchased:
            if post.module.module_code.upper() in completedPurchased:
                completedPurchased[post.module.module_code.upper()].append(post)
            else:
                completedPurchased[post.module.module_code.upper()] = [post]

        for request in completedRequests:
            if request.module.module_code.upper() in completedRequestsPurchased:
                completedRequestsPurchased[request.module.module_code.upper()].append(request)
            else:
                completedRequestsPurchased[request.module.module_code.upper()] = [request]

        template_values = {
            'completedSales': completedSales,
            'completedPurchased': completedPurchased,
            'completedRequestsPurchased': completedRequestsPurchased,
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url)}

        template = jinja_environment.get_template('completed.html')
        self.response.out.write(template.render(template_values))


app = webapp2.WSGIApplication([('/completed', Display)],
                              debug=True)