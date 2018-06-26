import TweetGetter as tg
import json
import datetime

def convertDateTime(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def return_tweet_summary(screen_name):
    report = tg.get_report(screen_name)
    return json.dumps(report, default = convertDateTime)