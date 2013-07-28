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

        posts_all = models.Post.all()
        pending = []
        status = False
        for post in posts_all:
            if post.status == "Pre-Completed" and post.seller is not None and post.seller.key() == currUser.key():
                pending.append(post)
                status = True

        template_values = {
            'currUser': currUser,
            'currSales': currSales,
            'currRequests': currRequests,
            'pending': pending,
            'status': status,
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url)}

        template = jinja_environment.get_template('currSale.html')
        self.response.out.write(template.render(template_values))


class Delete(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = self.request.url
        currPost = models.Post.get_by_id(int(url.split('/')[-1]))
        currRequest = models.Request.get_by_id(int(url.split('/')[-1]))
        if currPost:
            if currPost.status != "Pending":
                matched_request = currPost.matched_request
                matched_request.matched_posts.remove(currPost.key())
                if matched_request.matched_posts.__len__() == 0:
                    matched_request.status = "Pending"
                matched_request.put()
            currPost.delete()
        if currRequest:
            if currRequest.status != "Pending":
                for post_key in currRequest.matched_posts:
                    post = models.Post.get(post_key)
                    post.matched_request = None
                    post.status = "Pending"
                    post.put()
            currRequest.delete()


        time.sleep(0.5)
        self.redirect('/current')


class CompletedSales(webapp2.RequestHandler):
    def get(self):
        url = self.request.url
        currPost = models.Post.get_by_id(int(url.split('/')[-1]))
        if "isCompleted" in url:
            currPost.status = "Completed"
            currPost.put()
            if currPost.matched_request:
                currPost.matched_request.status = "Completed"
                currPost.matched_request.put()
            currSalesRecond = models.SaleRecord()
            currSalesRecond.book = currPost.book
            currSalesRecond.cost = currPost.cost
            currSalesRecond.put()
        else:
            if currPost.seller is not None:
                currPost.seller = None
                currPost.status = "Pending"
                currPost.put()
            else:
                matched_request = currPost.matched_request
                matched_request.matched_posts.remove(currPost.key())
                if matched_request.matched_posts.__len__() == 0:
                    matched_request.status = "Pending"
                else:
                    matched_request.status = "Matched"
                matched_request.put()
                currPost.status = "Pending"
                currPost.matched_request = None
                currPost.put()

        time.sleep(0.5)
        self.redirect('/current')


app = webapp2.WSGIApplication([('/current', Display),
                               ('/current/delete/.*?', Delete),
                               ('/current/completed/.*?', CompletedSales)],
                              debug=True)