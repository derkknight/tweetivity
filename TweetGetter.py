from twython import Twython
from twython import TwythonStreamer
from pandas import DataFrame, Series
from datetime import datetime, date, time, timedelta
import pandas as pd
import numpy as np
import twython
import time
import csv
import json

# Initialize 
with open('config.json', 'r') as file:
    config = json.load(file)
CONSUMER_KEY = config['CONSUMER_KEY']
CONSUMER_SECRET = config['CONSUMER_SECRET']
#twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET)

# Returns a list of user_ids of followers
def get_followers_of_user(screen_name):
    return twitter.get_followers_ids(screen_name = "nisellaneous")["ids"]

# Given a list of raw tweets, load in the data and return a pandas DataFrame
def load_data(tweets):
    df = DataFrame(data=tweets, columns=['Follower ID', 'Tweet ID', 'Timestamp'])
    df.set_index(pd.DatetimeIndex(df['Timestamp']), inplace=True)
    return df

# 
# Exception is used in the case of private account.
def get_follower_statuses(follower_id, list):
    try:
        for status in twitter.get_user_timeline(user_id=follower_id, include_rts=True, count=200):
            tweet_id = status["id"]
            timestamp = datetime.strptime(status["created_at"].encode('utf-8')[4:16], '%b %d %H:%M')
            tweet = []
            tweet.extend(follower_id, tweet_id, timestamp)
            list.append(str(follower_id) + ',' + str(tweet_id) + ',' + timestamp)
        #print list
    except twython.exceptions.TwythonAuthError:
        pass

def average_day(df):
    #df.groupby('Timestamp', [pd.cut(df.index.hour, pd.date_range("00:00", "23:59", freq="60min").time)]).mean()
    #print (pd.date_range("00:00", "23:59", freq="60min").time)
    #print (df.index.time)
    #print (pd.cut(df.index.time, pd.date_range("00:00", "23:59", freq="60min").time))
    #day_frame = get_tweets_by_day(df, 1).resample(rule='24H', closed='left', label='left', base = 17)
    #day_frame = get_tweets_by_day(df, 1).resample(rule='24H').sum()
    #print(get_tweets_by_day(df, 0))
    day_frame = get_tweets_by_day(df, 0).groupby(pd.Grouper(freq='1H')).nunique()
    day_frame = day_frame[(day_frame.T != 0).any()]
    return day_frame
    
def get_tweets_by_week(df, week):
    lol = datetime.today() - timedelta(weeks = week)
    #print df[(df.index > lol.strftime("%Y-%m-%d")) & (df.index <= datetime.today().strftime("%Y-%m-%d"))]
    return df[(df.index > lol.strftime("%Y-%m-%d")) & (df.index <= datetime.today().strftime("%Y-%m-%d"))]

# Helper function to convert string to datetime
def get_datetime_from_tweet(string):
    return datetime.strptime(string[4:20] + string[26:], '%b %d %H:%M:%S %Y')

# Using the DataFrame and given a day (0=Mon, 6=Sun), find all entries in that day
def get_tweets_by_day(df, day):
    #print (df)
    #print(df[df.index.weekday==day])
    return df[df.index.weekday==day]

# Using the DataFrame and given an hour, find all entries in that hour
def get_tweets_by_hour(df, hour):
    #print(df[df.index.hour==hour])
    return df[df.index.hour==hour]


###Crunch stuff
def get_report_x(screen_name):
    #followers = get_followers_of_user(screen_name)
    tweets = get_follower_statuses_canned()
    # get_follower_statuses()
    df = load_data(tweets)
    average_day(df)
    day = 0
    report_dict = {}
    while day < 6:
        day_frame = get_tweets_by_day(df, day)
        day_dict = []
        hour = 0
        while hour < 24:
            day_dict.append(get_number_of_users(get_tweets_by_hour(day_frame, hour)))
            hour += 1
        report_dict[day] = day_dict
        day += 1
    return report_dict

def get_report(screen_name):
    tweets = get_follower_statuses_canned()
    df = load_data(tweets)
    df = get_tweets_by_week(df, 7)
    df = average_day(df)
    report_dict = []
    hour = 0;
    while hour < 24:
        #get the mean of each hour
        mean = int(np.ceil(get_tweets_by_hour(df, hour)["Follower ID"].mean()))
        report_dict.append(mean)
        hour += 1
    return report_dict
    

# Gets the count of unique users.
def get_number_of_users(df):
    return df['Follower ID'].unique().size







def mainone():
    tweets = get_follower_statuses_canned()
    df = load_data(tweets)
    monday = get_tweets_by_day(df, 1)
    get_tweets_by_hour(monday, 1)

def get_follower_statuses_canned():
    tweets = []
    with open('sample_tweets.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        firstLine = True
        for row in spamreader:
            if firstLine:
                firstLine = False
                continue
            row[2] = get_datetime_from_tweet(row[2])
            tweets.append(row)
    return tweets


def initialize():
    tweets = get_follower_statuses_canned()
    report = get_report(tweets)

initialize()