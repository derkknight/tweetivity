from flask import Flask, render_template, request
from flask.logging import default_handler
import TweetMunger as tm
import logging
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
import datetime

app = Flask(__name__)

#Error handling
@app.errorhandler(Exception)
def unhandled_exception(e):
    return render_template('index.html', error = "An error has occurred. Please try again."), 500


@app.route("/")
def index():
    app.logger.info('LANDED: ' + request.remote_addr )
    return render_template('index.html')

@app.route("/<string:name>/<string:offset>")
def getFollowers(name, offset):
    tm.setTimezone(int(offset))
    data = tm.return_tweet_summary(name)
    return render_template('graph.html', data = data, name = name)

if __name__ == "__main__":
    handler = RotatingFileHandler('stats.log', backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run()