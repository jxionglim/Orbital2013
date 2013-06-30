import webapp2
import jinja2
import models
import os

from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect('/main')
        template_values = {
            'searchform': models.SearchForm(),
            'search': False,
            }
        template = jinja_environment.get_template('public_main.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        search_form = models.SearchForm(self.request.POST)
        if self.request.method == 'POST' and search_form.validate():
            search_cat = self.request.get('search_cat').rstrip()
            search_field = self.request.get('search_field').rstrip()

            tempResult = []
            results = []
            if search_cat == 'module_code':
                moduleList = models.Module.all()
                for module in moduleList:
                    if search_field in module.module_code:
                        tempResult.append(module)
                for records in tempResult:
                    allRecords = models.Post.all().filter('module', records)
                    for entry in allRecords:
                        results.append(entry)
            else:
                bookList = models.Book.all()
                for book in bookList:
                    if search_field in getattr(book, search_cat):
                        tempResult.append(book)
                for records in tempResult:
                    allRecords = models.Post.all().filter('book', records)
                    for entry in allRecords:
                        results.append(entry)

            template_values = {
                'searchform': search_form,
                'search': True,
                'searchResult': results,
                }
            template = jinja_environment.get_template('public_main.html')
            self.response.out.write(template.render(template_values))
        else:
            template_values = {
                'searchform': search_form,
                'search': False,
                }
            template = jinja_environment.get_template('public_main.html')
            self.response.out.write(template.render(template_values))


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
