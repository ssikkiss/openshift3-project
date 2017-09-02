from flask import Flask
from flask_apscheduler import APScheduler
import spv
import time
application = Flask(__name__)


class Config(object):
    JOBS = []
    SCHEDULER_API_ENABLED = True


def job1():
    print('hello,job')

    
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

application.config.from_object(Config())
scheduler = APScheduler()
# it is also possible to enable the API directly
# scheduler.api_enabled = True
scheduler.init_app(application)
scheduler.add_job(job1,'interval',seconds=20)
scheduler.start()
if __name__ == "__main__":
    print('hello,flask')
    application.run()
