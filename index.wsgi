import os
import hashlib
import cgi
import sae
sae.add_vendor_dir('vendor')
import web
import re
import funcIf4weixin
urls = (
    '/', 'Hello'
)

app_root = os.path.dirname(__file__)
templates_root = os.path.join(app_root, 'templates')
render = web.template.render(templates_root)

class Hello:
    def GET(self):
        data = web.input()
        echostr = data.echostr
        signature = data.signature
        timestamp = data.timestamp
        nonce = data.nonce
        token ='kamisama001'
        l = [token,timestamp,nonce]
        l.sort()
        s=l[0]+l[1]+l[2]	
	if hashlib.sha1(s).hexdigest() == signature:
		return echostr

    def POST(self):
	i = web.data()
        s=re.split('(<xml>)',i)
	data =s[1]+s[2]
    	worker = funcIf4weixin.msgHandler(data)
	return worker.response()
app = web.application(urls, globals()).wsgifunc()

application = sae.create_wsgi_app(app)