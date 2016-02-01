from datetime import datetime, timedelta
import re

import numpy as np
from PIL import Image
from wordcloud import WordCloud
import tweepy

import myauth


def main():
    api = get_twitter_api()
    replies = recent_replies(api, "BernieSanders")
    words = words_from_tweets(replies)
    bernie_mask = np.array(Image.open("bernie.png"))
    wordle = WordCloud(
        mask=bernie_mask,
        max_words=500,
        min_font_size=2,
        font_path="Roboto-Medium.ttf"
    ).generate(words).to_image()

    wordle.save("wordle.png")


def recent_replies(api, user, since_days_ago=1, max_tweets=1000):
    since_cutoff = datetime.today() - timedelta(days=since_days_ago)

    tweets = tweepy.Cursor(api.search, q=("@" + user), count=200).items(max_tweets)
    for tweet in tweets:
        if tweet.created_at < since_cutoff:
            return
        yield tweet


def words_from_tweets(tweets):
    ignore_words = {"RT"}
    
    def remove_users(s):
        return re.sub("@\w+", " ", s)

    def remove_urls(s):
        return re.sub(r"https?://\S+", "", s)

    text = " ".join(t.text for t in tweets)
    text = remove_urls(text)
    text = remove_users(text)
    words = re.sub("[^\w']", " ", text).split()
    words = (str(w) for w in words if w not in ignore_words)
    return " ".join(words)


def get_twitter_api():
    auth = tweepy.OAuthHandler(myauth.consumer_key, myauth.consumer_secret)
    auth.set_access_token(myauth.access_token, myauth.access_token_secret)
    return tweepy.API(auth)


if __name__ == '__main__':
    main()
