import webapp2
import models
from random import randint


class UpdateStatus(webapp2.RequestHandler):
    def get(self):
        newModule = models.Module()
        newModule.module_code = str(randint(1, 1000))
        #newModule.put()

app = webapp2.WSGIApplication([('/updateStatus', UpdateStatus)],
                      debug=True)