import webapp2
import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class MainPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('public_main.html')
        self.response.out.write(template.render())

class AboutPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('public_about.html')
        self.response.out.write(template.render())

class ContactPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('public_contact.html')
        self.response.out.write(template.render())

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/about_us', AboutPage),
                               ('/contact_us', ContactPage)],
                              debug=True)
