import os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import datamodel
import rippletransact
from google.appengine.ext import db


def form_validates(req):
    try:
        value = float(req.get("Quantity Owned")) > 0.0 and float(req.get("Minimum Exchange Rate")) > 0.0
    except:
        value = False
    return value


class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = {
            'output': [],
            }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        req = self.request
        
        template_values = {
            'bidder_name': req.get("Bidder Name"),
            'currency_owned': req.get("Currency Owned"),
            'currency_wanted': req.get("Currency Wanted"),
            'quantity_owned': req.get("Quantity Owned"),
            'min_exchange_rate': req.get("Minimum Exchange Rate"),
            'bids': req.get("Bids"),
            'output': ['Badly formatted bid.'],
            }
        if not form_validates(req):
            template_values['output'] = ['Badly formatted bid.']
        else:
            bids = req.get("Bids").splitlines()
            bids.append(u"%s,bid%d,%s,%s,%f,%f" % (
                    req.get("Bidder Name"),
                    len(bids),
                    req.get("Currency Owned"),
                    req.get("Currency Wanted"),
                    float(req.get("Quantity Owned")),
                    float(req.get("Minimum Exchange Rate"))))
            bid_class = []
            for bid in bids:
                bid = bid.split(",")
                offer = datamodel.Offer()
                
                offer.oauth_token = "fake oauth token"
                offer.bidder_name = bid[0]
                offer.currency_owned = bid[2]
                offer.currency_wanted = bid[3]
                offer.quantity_owned = float(bid[4])
                offer.min_exchange_rate = float(bid[5])
                
                bid_class.append(offer)
                
            db.put(bid_class)
            template_values['bids'] = "\n".join(bids)
            template_values['output'] = rippletransact.process_all_bids(bids)

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        self.response.out.write(bid_class[0].created)

application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()