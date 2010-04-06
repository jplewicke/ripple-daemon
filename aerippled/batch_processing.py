import os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
import rippletransact
import datamodel


def get_existing_offers():
    return db.GqlQuery("SELECT * FROM Offer ORDER BY created ASC")


class ProcessingPage(webapp.RequestHandler):
    def get(self):
        output = "cats"
        offers = get_existing_offers()
        template_values = {
            'output': ["bears"],
            }
        template_values['output'] = offers
        
        bids = []
        for offer in offers:
            bids.append(u"%s,%s,%s,%s,%f,%f" % (
                    offer.bidder_name,
                    offer.bidder_name,
                    offer.currency_owned,
                    offer.currency_wanted,
                    offer.quantity_owned,
                    offer.min_exchange_rate))
        template_values['output'] = rippletransact.process_all_bids(bids)
            
        
        path = os.path.join(os.path.dirname(__file__), 'processing.html')
        self.response.out.write(template.render(path, template_values))




application = webapp.WSGIApplication(
                                     [('/process', ProcessingPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()