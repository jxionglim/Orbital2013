import webapp2
import jinja2
import os
import models

from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))


class ShowStats(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        currUser = db.get(db.Key.from_path('User', user.email()))
        if not currUser.required_complete:
            self.redirect('/profile/edit')

        currBook = db.get(self.request.url.split('/')[-1])
        bookList = models.Book.all().filter('title =', currBook.title).filter('author =', currBook.author).filter('publisher =', currBook.publisher)
        headingArr = []
        editionArr = []
        totalRecords = []
        for books in bookList:
            if books.edition not in headingArr:
                headingArr.append(books.edition)
                editionArr.append(books.edition)
            allRecords = models.SaleRecord.all().filter('book =', books)
            for eachRecords in allRecords:
                totalRecords.append(eachRecords)
        headingArr.sort()
        editionArr.sort()
        headingArr = [str(x)+" e.d." for x in headingArr]
        headingArr.insert(0, 'Cost')

        costArr = []
        for records in totalRecords:
            if records.cost not in costArr:
                costArr.append(records.cost)
        costArr.sort()

        data = []
        for eachCost in costArr:
            eachCostArr = [str(eachCost)]
            for eachEdition in editionArr:
                bookEntry = models.Book.all().filter('title =', currBook.title).filter('author =', currBook.author).filter('publisher =', currBook.publisher).filter('edition =', eachEdition)[0]
                count = models.SaleRecord.all().filter('book =', bookEntry).filter('cost =', eachCost).count()
                eachCostArr.append(count)
            data.append(eachCostArr)

        data.insert(0, headingArr)
        template_values = {
            'title': currBook.title.title(),
            'author': currBook.author.title(),
            'data': data,
            'email': user.email(),
            'logout': users.create_logout_url(self.request.host_url),
            }
        template = jinja_environment.get_template('stats.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/stats/.*?', ShowStats)],
                              debug=True)