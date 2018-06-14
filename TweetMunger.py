import TweetGetter as tg
import json

def return_tweet_summary(screen_name):
    report = tg.get_report("")
    return json.dumps(report)