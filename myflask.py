from flask import Flask, flash, redirect, render_template, request, session, abort, Markup
import sqlite3
import ast
import os.path
import tweepy_streamer
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms.validators import InputRequired


db = "/Users/sarch/Desktop/TwitterAnalyzer/user.db"

app = Flask(__name__)
Bootstrap(app)


def get_top_tweets():
    conn = sqlite3.connect(db)
    #conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT tweetText from tweets")
    result = c.fetchall()
    tweets = []
    for tweet in result:
        tweets.append(tweet)
    conn.close()
    return tweets

def get_sentiment():
    conn = sqlite3.connect(db)
    #conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT sentiment from user")
    result = c.fetchall()
    tweets = []
    pos = 0
    neg = 0
    neut = 0
    for tweet in result:
        tweets.append(tweet[0])
        if tweet[0] > 0:
            pos = pos + 1
        elif tweet[0] < 0:
            neg = neg + 1
        elif tweet[0] == 0:
            neut = neut + 1

    total = len(tweets)
    conn.close()
    return round((pos/float(total))*100, 1), round((neg/float(total))*100, 1), round((neut/float(total))*100, 1)

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

@app.route("/sentiment")
def trends():
    pos, neg = get_sentiment()
    return render_template('sentiment.html', pos = pos, neg = neg)
    # sentiment = get_sentiment()
    # return render_template('sentiment.html', sentiment = sentiment)
    return "Sentiment"

@app.route('/data')
def pie_sent():
    pos, neg, neut = get_sentiment()
    values = [pos,neg, neut]
    labels = ['Negative', 'Positive', 'Neutral']
    colors = ["#F7464A", "#46BFBD", "#F6E481"]
    pie_labels = labels
    pie_values = values

    pos2, neg2, neut2 = get_sentiment()
    values2 = [pos2,neg2, neut2]
    labels2 = ['Negative', 'Positive', 'Neutral']
    colors2 = ["#F7464A", "#46BFBD", "#F6E481"]
    pie_labels = labels2
    pie_values = values2

    return render_template('pie_chart.html', title='Positive vs Negative Tweets for ', max=100, set=zip(values, labels, colors), set2=zip(values2, labels2, colors2))

if __name__ == "__main__":
    app.run(debug = True)
