from flask import Flask, flash, redirect, render_template, request, session, abort
import sqlite3
import ast
import os.path
import tweepy_streamer

db = "/Users/sarch/Desktop/TwitterAnalyzer/twitter.db"

app = Flask(__name__)

def get_top_tweets():
    conn = sqlite3.connect(db)
    #conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * from tweets")
    result = c.fetchall()
    tweets = []
    for tweet in result:
        tweets.append(tweet)
    conn.close()
    return tweets

@app.route('/')
def my_form():
    return render_template('my-form.html')

@app.route('/', methods=['POST'])
def my_form_post():
    print ("myformpost")
    text = request.form['text']
    processed_text = text.upper()
    tweepy_streamer.main(processed_text)
    return processed_text

@app.route("/top_tweets")
def top_tweets():
    tweets = get_top_tweets()
    return render_template('top_tweets.html', tweets = tweets)

@app.route("/trends")
def trends():
    return "Trending On Twitter:"

if __name__ == "__main__":
    app.run(debug = True)
