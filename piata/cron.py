import webapp2
import models
import re

from google.appengine.api import mail


class UpdateStatus(webapp2.RequestHandler):
    def get(self):
        requests = models.Request.all().order('-request_date')
        posts = models.Post.all()

        for request in requests:
            cost = map(int, re.findall(r'\d+', request.cost_range))

            if cost.__len__() == 1:
                cost_lower = cost.__getitem__(0)
                cost_upper = cost.__getitem__(0)
            else:
                cost_lower = cost.__getitem__(0)
                cost_upper = cost.__getitem__(1)

            for post in posts:
                if request.module.module_code == post.module.module_code and request.book.title == post.book.title and request.book.author == post.book.author and request.book.publisher == post.book.publisher and request.book.edition == post.book.edition and cost_lower <= post.cost <= cost_upper and post.status != "Matched" and post.status != "Pre-Completed" and post.status != "Completed" and post.user.key() != request.user.key() and post.seller is None:
                    post.status = "Matched"
                    post.matched_request = request
                    post.put()
                    if post.key() not in request.matched_posts:
                        request.matched_posts.append(post.key())

            if request.matched_posts.__len__() != 0:
                if request.status != "Pre-Completed" and request.status != "Completed":
                    request.status = "Matched"
                    request.put()

                    url = "http://piata-sg.appspot.com/matched/" + str(request.key().id())
                    message = mail.EmailMessage()
                    message.sender = "teamlupus.13@gmail.com"
                    message.to = str(request.user.key().name())
                    message.subject = "A match has been found for " + str(request.book.title.title())
                    message.body = """
A match has been found for the book that you have requested.

Please click the following link below to access it.

%s

With Regards,

Team Lupus
                    """ % url

                    message.send()

app = webapp2.WSGIApplication([('/updateStatus', UpdateStatus)],
                      debug=True)