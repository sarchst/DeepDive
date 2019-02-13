from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
import re
import sqlite3
import twitter_credentials
import json
import inspect



class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id = self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id = self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Curor(self.twitter_client.home_timeline, id = self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


class TwitterAuthenticator():

    def authenticate_twitter_app(self):
            auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
            auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
            return auth

class TwitterStreamer():
    """
    Class for streaming and processing life tweets
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename,hash_tag_list):
        # This handles Twitter authentication and connection to the TwitterStreamer
        # streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        stream.filter(track=hash_tag_list)


class TwitterListener(StreamListener):
    def __init__ (self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data): #take in data from streamlistener and do something with it
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                    tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    def on_error(self, status):# gets called if there is an on_error
        if status == 420:
            #returning false on data method incase rate limmit occurs
            return False
        print(status)


class TweetStreamListener(StreamListener):
    # When data is received
    def on_data(self, data):
        twitter_client = TwitterClient()
        tweet_analyzer = TweetAnalyzer()

        api = twitter_client.get_twitter_client_api()

        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        c.execute("SELECT max(rowid) from tweets")
        n = c.fetchone()[0]

        if (n != None and n > 10):
            return False;

        try:

            tweet = json.loads(data)

            if not tweet['retweeted'] and 'RT @' not in tweet['text']:

                user_profile = api.get_user(tweet['user']['screen_name'])

                # assign all data to Tweet object
                tweet_data = Tweet(
                    str(tweet['text'].encode('utf-8')),
                    tweet['user']['screen_name'],
                    user_profile.followers_count,
                    tweet['created_at'],
                    tweet['user']['location'],
                    tweet['lang'])

                # Insert that data into the DB
                if tweet_data.lang == "en":
                    #tweet_data.insertTweet()
                    print(tweet_data.text)
                    c.execute("INSERT INTO tweets (tweetText, user, followers, date, location, lang, sentiment) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (tweet_data.text, tweet_data.user, tweet_data.followers, tweet_data.date, tweet_data.location, tweet_data.lang, tweet_analyzer.analyze_sentiment(tweet_data.text)))
                    conn.commit()

                    print("success")

                else:
                    print(tweet_data.lang)


        # Let me know if something bad happens
        except Exception as e:
            print(e)

            pass

        return True




class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing ocntent from tweets
    """
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data = [tweet.text for tweet in tweets], columns = ['tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        return df

    def create_db(self):
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE tweets
            (tweetText text,
            user text,
            followers integer,
            date text,
            location text,
            lang text,
            sentiment integer)''')
        conn.commit()
        conn.close()

class Tweet():
    # Data on the tweet
    def __init__(self, text, user, followers, date, location, lang):
        self.text = text
        self.user = user
        self.followers = followers
        self.date = date
        self.location = location
        self.lang = lang

    def clean_tweet(self):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", self.text).split())

    # Inserting that data into the DB
    def insertTweet(self):
        self.text = self.clean_tweet()
        c.execute("INSERT INTO tweets (tweetText, user, followers, date, location, lang, sentiment) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (self.text, self.user, self.followers, self.date, self.location, self.lang, ))
        conn.commit()


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None

def delete_all_tasks(conn):
    """
    Delete all rows in the tasks table
    :param conn: Connection to the SQLite database
    :return:
    """
    sql = 'DELETE FROM tweets'
    cur = conn.cursor()
    cur.execute(sql)



#if __name__ == "__main__":
def main(text_input):
    db = "/Users/sarch/Desktop/TwitterAnalyzer/twitter.db"
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    tweet_analyzer.create_db()


    # create a database connection and clear database
    conn = create_connection(db)
    with conn:
        delete_all_tasks(conn);


    api = twitter_client.get_twitter_client_api()
    tweets = api.user_timeline(screen_name="MarinaAdshade", count=10)
    df = tweet_analyzer.tweets_to_data_frame(tweets)
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
    print(df.head(10))

    # Run the stream!
    l = TweetStreamListener()
    stream = Stream(twitter_client.auth, l)
    # Filter the stream for these keywords
    stream.filter(track=[text_input])
