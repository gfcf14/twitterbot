# libraries to log in to twitter
import logging
import os
import random
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

# check the latest mentions of the bot, and reply to each. For now, via a simple random number generator
def check_mentions(api, keywords, since_id):
  new_since_id = since_id

  # iterate over the 20 most recent mentions of the bot according to the since_id
  for tweet in tweepy.Cursor(api.mentions_timeline, since_id=since_id).items():
    # get the new since_id in order to avoid searching on older tweets
    new_since_id = max(tweet.id, new_since_id)

    # to avoid tweets that are replies
    if tweet.in_reply_to_status_id is not None:
      continue
    if any(keyword in tweet.text.lower() for keyword in keywords):
      # get the mentioner's handle
      mentioner = tweet.author.screen_name
      logger.info('Found answerable tweet from ' + mentioner + ' with text: ' + tweet.text)
      rand_num = random.randint(1,101)

      # reply with a mention to the user
      api.update_status(
        status="@" + mentioner + " Here is your number: " + str(rand_num),
        in_reply_to_status_id=tweet.id,
      )
  return new_since_id

# main function
def main():
  # declare api
  api = create_api()
  # declare variable to get latest post id
  since_id = get_latest_post(api)

  while True:
    since_id = check_mentions(api, ["random"], since_id)
    logger.info('Waiting for someone to mention me...')
    time.sleep(60)

if __name__ == "__main__":
  main()