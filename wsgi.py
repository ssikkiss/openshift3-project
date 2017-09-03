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
            'args': (600,1),
            'trigger': 'interval',
            'seconds': 10
        }
    ]

    SCHEDULER_API_ENABLED = True


def job1(runtime,a):
#ret=node.work(runtime)
#print(ret)
    print(runtime)
    
@application.route("/")
def hello():
    return "Hello World!ggggggggggggghhhhhg"
@application.route("/test")
def test():
    ret='<font size=14>server count:'+str(len(node.servers))
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
#scheduler.start()
@application.route('/stop')
def stopjob():
    scheduler.shutdown()
    return 'stop susscessful,running: '+str(scheduler.running)
@application.route('/start')
def startjob():
    scheduler.start()
    return 'start susscessful,running: '+str(scheduler.running)
if __name__ == "__main__":
    print('hello,flask')
    application.run()
