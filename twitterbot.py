# libraries to log in to twitter
import json
import logging
import os
import random
import requests
import time
import tweepy
from dotenv import find_dotenv, load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# creates the tweepy api based on environment credentials
def create_api():
  # load key credentials from .env file
  load_dotenv(find_dotenv(), override=True)

  # get all necessary credentials
  api_key = os.getenv('API_KEY')
  secret_key = os.getenv('SECRET_KEY')
  access_token = os.getenv('ACCESS_TOKEN')
  secret_token = os.getenv('SECRET_TOKEN')

  # set authentication with the keys
  auth = tweepy.OAuthHandler(api_key, secret_key)
  auth.set_access_token(access_token, secret_token)

  # prepare api
  api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
  user = api.me()

  logger.info('Successfully created API for ' + user.screen_name)

  return api

# gets the last post id made by the bot
def get_latest_post(api):
  return api.me().status.id

# gets a random joke from the rapidapi
def get_joke(key):
  extra_text_len = 21
  max_username_len = 15
  max_tweet_len = 280
  url = 'https://joke3.p.rapidapi.com/v1/joke'

  payload = '{}'
  headers = {
    'x-rapidapi-key': key,
  }
  params = {}

  joke_text = ''

  while True:
    response = requests.request("GET", url, data=payload, headers=headers, params=params)
    json_dict = json.loads(response.text)
    joke_text = json_dict.get('content')

    # ensure the fetched joke doesn't exceed the twitter max length
    if (len(joke_text) + extra_text_len + max_username_len) < max_tweet_len:
      break

  return joke_text

# check the latest mentions of the bot, and reply to each. For now, via a simple random number generator
def check_mentions(api, since_id, rapid_api_key):
  new_since_id = since_id

  # iterate over the 20 most recent mentions of the bot according to the since_id
  for tweet in tweepy.Cursor(api.mentions_timeline, since_id=since_id).items():
    # get the mentioner's handle
    mentioner = tweet.author.screen_name

    # get the new since_id in order to avoid searching on older tweets
    new_since_id = max(tweet.id, new_since_id)

    # to avoid tweets that are replies
    if tweet.in_reply_to_status_id is not None:
      continue

    request = tweet.text.lower()
    reply = ''

    if 'joke please' in request:
      reply = '@' + mentioner + ' Here is your joke: ' + str(get_joke(rapid_api_key))
    else:
      reply = 'Hi, @' + mentioner + ' ! I don\'t understand your request. If you write the words \'joke please\', somewhere, I\'ll send you a good one!!'

    logger.info('Replying: ' + reply)

    # reply to the user
    api.update_status(status=reply, in_reply_to_status_id=tweet.id)

  return new_since_id

# main function
def main():
  # declare api
  api = create_api()
  # declare variable to get latest post id
  since_id = get_latest_post(api)
  # get the RapidApi key
  rapid_api_key = os.getenv('RAPID_API_KEY')

  while True:
    since_id = check_mentions(api, since_id, rapid_api_key)
    logger.info('Waiting for someone to mention me...')
    time.sleep(20)

if __name__ == "__main__":
  main()