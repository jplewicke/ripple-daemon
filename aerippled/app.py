import os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import rippletransact


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
            bids.append(u"bid%d|%s,%s,%s,%f,%f" % (
                    len(bids),
                    req.get("Bidder Name"),
                    req.get("Currency Owned"),
                    req.get("Currency Wanted"),
                    float(req.get("Quantity Owned")),
                    float(req.get("Minimum Exchange Rate"))))
            template_values['bids'] = "\n".join(bids)
            template_values['output'] = rippletransact.process_all_bids(bids)

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()