from flask import Flask, render_template
import TweetMunger as tm
app = Flask(__name__)
 
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/<string:name>/")
def getFollowers(name):
    data = tm.return_tweet_summary(name)
    return render_template('graph.html', data = data)

if __name__ == "__main__":
    app.run()