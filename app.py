import web
from web import form
import rippletransact



urls = (
  '/', 'index'
)

app = web.application(urls, globals())

myform = form.Form(
    form.Textbox("Bidder Name",
        form.notnull),
    form.Textbox("Currency Owned"    ,
            form.notnull),
    form.Textbox("Quantity Owned",
        form.notnull,
        form.Validator('Must be more than 0', lambda x:float(x)>0)),        
    form.Textbox("Currency Wanted"    ,
            form.notnull),
    form.Textbox("Minimum Exchange Rate",
        form.notnull,
        form.Validator('Must be more than 0', lambda x:float(x)>0)),
    form.Textarea('Bids'))



class index:
    def GET(self):
        form = myform()
        render = web.template.render('templates')
        print dir(form['Bids'])
        return render.index(form,'')
        
    def POST(self):
        form = myform()
        render = web.template.render('templates')
        if not form.validates():
            return render.index(form,'')
        else:
            bids = form['Bids'].value.splitlines()
            bids.append(u"bid%d|%s,%s,%s,%f,%f" % (
                    len(bids),
                    form['Bidder Name'].value, 
                    form['Currency Owned'].value,
                    form['Currency Wanted'].value,
                    float(form['Quantity Owned'].value),
                    float(form["Minimum Exchange Rate"].value)))
            form['Bids'].set_value("\n".join(bids))
            return render.index(form, rippletransact.process_all_bids(bids))



if __name__ == "__main__": app.run()
