from google.appengine.ext import db

class Offer(db.Model):
    oath_token = db.StringProperty()
    bidder_name = db.StringProperty()
    currency_owned = db.StringProperty()
    currency_wanted = db.StringProperty()
    quantity_owned = db.FloatProperty()
    min_exchange_rate = db.FloatProperty()
    created = db.DateTimeProperty(auto_now_add=True)

class ExchangeCycle(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)

class Allocation(db.Model):
    cycle = db.ReferenceProperty(ExchangeCycle)
    quantity = db.FloatProperty()
    exchange_rate = db.FloatProperty()
    created = db.DateTimeProperty(auto_now_add=True)