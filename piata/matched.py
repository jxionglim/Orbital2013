import webapp2
import jinja2
import os
import models
import time

from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class Matched(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if not currUser.required_complete:
            self.redirect('/profile/edit')

        url = self.request.url
        currRequest = models.Request.get_by_id(int(url.split('/')[-1]))
        posts = []
        if currRequest is not None:
            if currRequest.status == "Matched" or currRequest.status == "Pre-Completed":
                post_keys = currRequest.matched_posts
                for post_key in post_keys:
                    post = models.Post.get(post_key)
                    posts.append(post)

        status = False

        for post in posts:
            if post.status == "Pre-Completed":
                status = True
                break

        template_values = {
            'email': user.email(),
            'posts': posts,
            'status': status,
            'logout': users.create_logout_url(self.request.host_url)}

        template = jinja_environment.get_template('matched.html')
        self.response.out.write(template.render(template_values))


class RequestingNow(webapp2.RequestHandler):
    def get(self):
        url = self.request.url
        currPost = models.Post.get_by_id(int(url.split('/')[-1]))
        currPost.status = "Pre-Completed"
        currPost.put()

        currRequest = models.Request.get_by_id(int(currPost.matched_request.key().id()))
        currRequest.status = "Pre-Completed"
        currRequest.put()

        time.sleep(0.5)
        self.redirect('/matched/' + str(currPost.matched_request.key().id()))


app = webapp2.WSGIApplication([('/matched/request/.*?', RequestingNow),
                               ('/matched/.*?', Matched)],
                              debug=True)