import json
import tempfile
from datetime import datetime, timedelta
import os
import re

import numpy as np
from PIL import Image
import tweepy
from wordcloud import WordCloud


def main():
    if 'ON_HEROKU' in os.environ:
        twitter = Twitter.from_env()
    else:
        twitter = Twitter.from_myauth()

    with open('twitter_users.json') as f:
        users = json.load(f)['users']

    wordles = (daily_user_wordle(twitter, u) for u in users)

    with tempfile.TemporaryDirectory() as temp_dir:
        for user, wordle in zip(users, wordles):
            wordle_path = os.path.join(temp_dir, '{}_wordle.png'.format(user))
            wordle.save(wordle_path)
            status = 'Daily mention wordle for @{}'.format(user)
            twitter.tweet(wordle_path, status=status)


class Twitter:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    @classmethod
    def from_env(cls):
        return cls(
            consumer_key=os.environ.get('TWITTER_CONSUMER_KEY'),
            consumer_secret=os.environ.get('TWITTER_ACCESS_TOKEN'),
            access_token=os.environ.get('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
        )

    @classmethod
    def from_myauth(cls):
        import myauth
        return cls(
            consumer_key=myauth.consumer_key,
            consumer_secret=myauth.consumer_secret,
            access_token=myauth.access_token,
            access_token_secret=myauth.access_token_secret
        )

    def mentions_since(self, user, days_ago, max_tweets=1000):
        since_cutoff = datetime.today() - timedelta(days=days_ago)

        tweets = tweepy.Cursor(self.api.search, q=('@' + user), count=200).items(max_tweets)
        for tweet in tweets:
            if tweet.created_at < since_cutoff:
                return
            yield tweet

    def tweet(self, img_path, status):
        self.api.update_with_media(img_path, status=status)


def daily_user_wordle(twitter, username):
    mentions = twitter.mentions_since(username, days_ago=1)
    words = words_from_tweets(mentions, ignore_words={'RT'})
    mask_file = os.path.join('assets', username + '.png')
    mask = np.array(Image.open(mask_file))
    return WordCloud(
        mask=mask,
        max_words=500,
        min_font_size=2,
        font_path=os.path.join('assets', 'Roboto-Medium.ttf')
    ).generate(words).to_image()


def words_from_tweets(tweets, ignore_words):
    remove_urls = lambda s: re.sub(r'https?://\S+', '', s)
    remove_users = lambda s: re.sub('@\w+', ' ', s)

    text = ' '.join(t.text for t in tweets)
    text = remove_urls(text)
    text = remove_users(text)
    words = re.sub("[^\w']", ' ', text).split()
    words = (str(w) for w in words if w not in ignore_words)
    return ' '.join(words)


if __name__ == '__main__':
    main()
