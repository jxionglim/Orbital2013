import webapp2
import jinja2
import models
import os
import logging

from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class MainPage(webapp2.RequestHandler):
    def get(self):
        if self.request.get('search_cat').rstrip() == "":
            user = users.get_current_user()
            if user:
                self.redirect('/main')
            template_values = {
                'searchform': models.SearchForm(),
                'search': False
                }
            template = jinja_environment.get_template('public_main.html')
            self.response.out.write(template.render(template_values))
        else:
            search_form = models.SearchForm(self.request.GET)
            if self.request.method == 'GET' and search_form.validate():
                search_cat = self.request.get('search_cat').rstrip()
                search_field = self.request.get('search_field').rstrip()

                tempResult = []
                results = []
                if search_cat == 'module_code':
                    moduleList = models.Module.all()
                    for module in moduleList:
                        if search_field.upper() in module.module_code:
                            tempResult.append(module)
                    for records in tempResult:
                        allRecords = models.Post.all().filter('module', records).filter('status !=', 'Pre-Completed').filter('status !=', 'Completed')
                        for entry in allRecords:
                            results.append(entry)
                else:
                    bookList = models.Book.all()
                    for book in bookList:
                        if search_field.lower() in getattr(book, search_cat):
                            tempResult.append(book)
                    for records in tempResult:
                        allRecords = models.Post.all().filter('book', records).filter('status !=', 'Pre-Completed').filter('status !=', 'Completed')
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


class AdvanceSearchPage(webapp2.RequestHandler):
    def get(self):
        if self.request.get('module_code_type').rstrip() == "":
            user = users.get_current_user()
            if user:
                self.redirect('/main')
            template_values = {
                'searchform': models.AdvSearchForm(),
                'search': False,
                }
            template = jinja_environment.get_template('public_adv_search.html')
            self.response.out.write(template.render(template_values))
        else:
            search_form = models.AdvSearchForm(self.request.GET)
            if self.request.method == 'GET' and search_form.validate():
                module_code = self.request.get('module_code').rstrip()
                module_code_type = self.request.get('module_code_type').rstrip()
                title = self.request.get('title').rstrip()
                title_type = self.request.get('title_type').rstrip()
                author = self.request.get('author').rstrip()
                author_type = self.request.get('author_type').rstrip()
                publisher = self.request.get('publisher').rstrip()
                publisher_type = self.request.get('publisher_type').rstrip()
                edition = int(self.request.get('edition').rstrip()) if self.request.get('edition').rstrip() != "" else self.request.get('edition').rstrip()
                edition_type = self.request.get('edition_type').rstrip()
                cost = int(self.request.get('cost').rstrip()) if self.request.get('cost').rstrip() != "" else self.request.get('cost').rstrip()
                cost_type = self.request.get('cost_type').rstrip()
                usermail = self.request.get('usermail').rstrip()

                exactDict, containDict = {}, {}
                postList, postListTemp = [], []

                if module_code != "":
                    if module_code_type == 'exact':
                        exactDict['module_code'] = module_code
                    else:
                        containDict['module_code'] = module_code
                if title != "":
                    if title_type == 'exact':
                        exactDict['title'] = title
                    else:
                        containDict['title'] = title
                if author != "":
                    if author_type == 'exact':
                        exactDict['author'] = author
                    else:
                        containDict['author'] = author
                if publisher != "":
                    if publisher_type == 'exact':
                        exactDict['publisher'] = publisher
                    else:
                        containDict['publisher'] = publisher

                prePostList = models.Post.all().filter('status !=', 'Pre-Completed').filter('status !=', 'Completed')
                for post in prePostList:
                    postList.append(post)

                for key, value in exactDict.items():
                    if key == "module_code":
                        for post in postList:
                            if post.module.module_code != value.upper():
                                postListTemp.append(post)
                    else:
                        for post in postList:
                            if getattr(post.book, key) != value.lower():
                                postListTemp.append(post)
                    postList = [item for item in postList if item not in postListTemp]
                    postListTemp = []

                for key, value in containDict.items():
                    if key == "module_code":
                        for post in postList:
                            if value.upper() not in post.module.module_code:
                                postListTemp.append(post)
                    else:
                        for post in postList:
                            if value.lower() not in getattr(post.book, key):
                                postListTemp.append(post)
                    postList = [item for item in postList if item not in postListTemp]
                    postListTemp = []

                if edition != "":
                    if edition_type == "=":
                        for post in postList:
                            if post.book.edition != edition:
                                postListTemp.append(post)
                    if edition_type == ">":
                        for post in postList:
                            if post.book.edition <= edition:
                                postListTemp.append(post)
                    if edition_type == "<":
                        for post in postList:
                            if post.book.edition >= edition:
                                postListTemp.append(post)
                    postList = [item for item in postList if item not in postListTemp]
                    postListTemp = []

                if cost != "":
                    if cost_type == "=":
                        for post in postList:
                            if post.cost != cost:
                                postListTemp.append(post)
                    if cost_type == ">":
                        for post in postList:
                            if post.cost <= cost:
                                postListTemp.append(post)
                    if cost_type == "<":
                        for post in postList:
                            if post.cost >= cost:
                                postListTemp.append(post)
                    postList = [item for item in postList if item not in postListTemp]
                    postListTemp = []

                conditionList = [self.request.get('condition_highlights').rstrip()]
                conditionList.append(self.request.get('condition_stains').rstrip())
                conditionList.append(self.request.get('condition_writings').rstrip())
                conditionList.append(self.request.get('condition_dog_eared').rstrip())
                conditionList.append(self.request.get('condition_torn').rstrip())
                conditionList.append(self.request.get('condition_wrapped').rstrip())
                conditionList.append(self.request.get('condition_not_used_once').rstrip())
                conditionList = [item for item in conditionList if item != ""]

                if len(conditionList) != 0:
                    for post in postList:
                        if len(set(conditionList) & set(post.condition)) == 0:
                            postListTemp.append(post)

                postList = [item for item in postList if item not in postListTemp]

                if usermail != "":
                    postList = [item for item in postList if item.user.key().name() == usermail]

                template_values = {
                    'searchform': search_form,
                    'searchResult': postList,
                    'search': True,
                    }
                template = jinja_environment.get_template('public_adv_search.html')
                self.response.out.write(template.render(template_values))
            else:
                template_values = {
                    'searchform': search_form,
                    'search': False,
                    }
                template = jinja_environment.get_template('public_adv_search.html')
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
                               ('/advsearch', AdvanceSearchPage),
                               ('/about_us', AboutPage),
                               ('/contact_us', ContactPage)],
                              debug=True)
