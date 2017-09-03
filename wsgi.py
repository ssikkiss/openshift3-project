from flask import Flask
from flask_apscheduler import APScheduler
import spv
import time
application = Flask(__name__)

class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': 'wsgi:job1',
            'args': (300,),
            'trigger': 'interval',
            'seconds': 600
        }
    ]

    SCHEDULER_API_ENABLED = True


def job1(runtime):
    node=spv.node()
    ret=node.work(runtime)
    print('============================')
    
@application.route("/")
def hello():
    return "Hello World!ggggggggggggghhhhhg"
@application.route("/test")
def test():
    ret='<font size=14>'
    ret+=spv.search()
    ret+='</font>'
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
    if scheduler.running:
        scheduler.shutdown()
    return 'stop susscessful,running: '+str(scheduler.running)
@application.route('/start')
def startjob():
    if not scheduler.running:
        scheduler.start()
    return 'start susscessful,running: '+str(scheduler.running)
if __name__ == "__main__":
    print('hello,flask!')
    application.run()
