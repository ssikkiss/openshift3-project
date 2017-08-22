from flask import Flask
import spv
application = Flask(__name__)

@application.route("/")
def hello():
    return "Hello World!ggggggggggggghhhhhg"
@application.route("/test")
def test():
    n=spv.node()
    ret='<font size=14>server count:'+str(len(n.servers))
    ret+=n.work()
    ret+=spv.search()
    ret+='</font>'
    return ret
    return "Hello World!ggggggggggggghhhhhg"

if __name__ == "__main__":
    application.run()
