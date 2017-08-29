from flask import Flask
import spv
import time
application = Flask(__name__)


@application.route("/")
def hello():
    return "Hello World!ggggggggggggghhhhhg"
@application.route("/test")
def test():
    n=spv.node()
    ret='<font size=14>server count:'+str(len(n.servers))
    t=time.time()
    ret+=n.work()
    ret+=spv.search()
    t=time.time()-t
    ret+='<br>take time:'+str(t)
    ret+='sec.</font>'
    return ret
    return "Hello World!ggggggggggggghhhhhg"

if __name__ == "__main__":
    application.run()
