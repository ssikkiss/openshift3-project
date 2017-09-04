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
            'args': (300,),
            'trigger': 'interval',
            'seconds': 6
        }
    ]

    SCHEDULER_API_ENABLED = True


def job1(runtime):
    print('job1')
    return
    node.work(runtime)
    print('============================')
    
application.config.from_object(Config())
scheduler = APScheduler()
# it is also possible to enable the API directly
#scheduler.api_enabled = True

@application.route("/")
def hello():
    ret='<font size=13><ul>------ cron info --------'
    ret+='<li>running = '+str(scheduler.running)
    ret+='</li></ul>'
    ret+= node.getinfo()
    ret+='</font>'
    return ret
@application.route("/search")
def test():
    ret='<font size=14>'
    ret+=node.search()
    ret+='</font>'
    return ret
    return "Hello World!ggggggggggggghhhhhg"


@application.route('/start')
def startscheduler():
    node.flagcontinue=True
    scheduler.init_app(application)
    scheduler.start()
    return 'start susscessful'
@application.route('/pause')
def pausejob():
    node.flagcontinue=False
    scheduler.pause_job('job1')
    return 'pause susscessful'
@application.route('/resume')
def resumejob():
    node.flagcontinue=True
    scheduler.resume_job('job1')
    return 'resume susscessful'
if __name__ == "__main__":
    print('hello,flask!')
    application.run()
