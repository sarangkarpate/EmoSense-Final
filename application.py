import json
import thread

#from TweetListener import *
from flask import Flask, render_template, jsonify

from TweetHandler import TwitterHandler

#----------------------------------------
# News Fetching and Handling API
from news import NewsHandler
from news.NewsListener import *
#----------------------------------------


# function that pulls tweets from twitter
def startTwitterRequests():
    print "Starting the wrong function"
    startStream()


def fetchNewsArticles():
    startFetch()

# EB looks for an 'application' callable by default.
application = Flask(__name__)

@application.route('/')
def api_root():
    return render_template('index.html')
    # return 'Welcome'

@application.route('/search/<keyword>')
def searchKeyword(keyword):
    searchTweets = TwitterHandler()
    result = searchTweets.getTweets(keyword)
    return jsonify(result)

@application.route('/search/<keyword>/<distance>/<latitude>/<longitude>')
def searchKeywordWithDistance(keyword, distance, latitude, longitude):
    searchTweets = TwitterHandler()
    result = searchTweets.getTweetsWithDistance(keyword, distance, latitude, longitude)
    return jsonify(result)

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    #thread.start_new_thread(startTwitterRequests, ())
    thread.start_new_thread(fetchNewsArticles,())
    application.debug = True
    application.run()