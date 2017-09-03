from flask import Flask
from flask_apscheduler import APScheduler
import spv
import time
application = Flask(__name__)
node=spv.node()

class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': 'wsgi:job1',
            'args': (600,),
            'trigger': 'interval',
            'seconds': 1000
        }
    ]

    SCHEDULER_API_ENABLED = True


def job1(runtime):
#ret=node.work(runtime)
#print(ret)
    print(runtime)
    
@application.route("/")
def hello():
    return "Hello World!ggggggggggggghhhhhg"
@application.route("/test")
def test():
    ret='<font size=14>server count:'+str(len(n.servers))
    t=time.time()
    ret+=spv.search()
    t=time.time()-t
    ret+='<br>take time:'+str(t)
    ret+='sec.</font>'
    return ret
    return "Hello World!ggggggggggggghhhhhg"


application.config.from_object(Config())
scheduler = APScheduler()
# it is also possible to enable the API directly
#scheduler.api_enabled = True
scheduler.init_app(application)
scheduler.start()
#scheduler.pause_job('job1')
@application.route('/pause')
def pause():
    ret=scheduler.pause_job('job1')
    return 'pause seuccessful'
@application.route('/resume')
def resume():
    ret=scheduler.resume_job('job1')
    return 'resume seuccessful'
if __name__ == "__main__":
    print('hello,flask')
    application.run()
