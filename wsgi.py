from flask import Flask
import urllib.request
application = Flask(__name__)

@application.route("/")
def hello():
    ret='hello'
    return ret
@application.route("/site/<site>")
def site():
    f=open('site.txt','wt')
    f.turncate(0)
    f.writeline(site)
    f.close()
    return 'site:'+site
@application.route("/ladder")
def ladder():
    f=open('site.txt','rt')
    site=f.readline()
    f.close()
    response=urllib.request.urlopen(site)
    ret=response.read()
    return ret
@application.route("/ladder/<path>")
def ladder():
    f=open('site.txt','rt')
    site=f.readline()
    f.close()
    response=urllib.request.urlopen(site+'/'+path)
    ret=response.read()
    return ret

if __name__ == "__main__":
    print('hello,flask')
    application.run()
