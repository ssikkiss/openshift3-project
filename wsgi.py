from flask import Flask
application = Flask(__name__)

@application.route("/")
def hello():
    return "<center><h2>Hello World!</h2></center>"

if __name__ == "__main__":
    application.run()
