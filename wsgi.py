from flask import Flask
import urllib.request
import pornhub
application = Flask(__name__)

@application.route("/")
def hello():
    search_keywords = []
    client = pornhub.PornHub(search_keywords)

    ret=''
    for video in client.getVideos(10,page=2):
        ret+='<br>'+video
    
    for photo_url in client.getPhotos(5):
        ret+='<br>'+photo_url

    

    return ret




if __name__ == "__main__":
    print('hello,flask')
    application.run()
