# libraries to log in to twitter
import tweepy
import time
import os
from dotenv import find_dotenv, load_dotenv

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

# twitter bot code
user = api.me()

print(user.screen_name)
# api.update_status("Hi!, I'm Little Green Sparky!!")