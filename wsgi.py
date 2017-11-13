from flask import Flask
application = Flask(__name__)

@application.route("/")
def hello():
    ret='hello'
    return ret
if __name__ == "__main__":
    print('hello,flask')
    application.run()
