import TweetGetter as tg
import json

def return_tweet_summary(screen_name):
    report = tg.get_report(screen_name)
    return json.dumps(report)