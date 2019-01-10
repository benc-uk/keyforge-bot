#!/usr/bin/python3
 
import praw
import re
import sqlite3
import signal
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from pprint import pprint

# Start up and config stuff
load_dotenv()

#DB_PATH        = './data/'
#DB_NAME        = 'replies.db'
CARD_DB        = './cards.json'
SUBREDDIT_NAME = os.getenv('SUBREDDIT_NAME', 'testingground4bots') 
SKIP_OLD       = True #bool(os.getenv('SKIP_OLD', 'True'))

print("### Starting KeyForgeCardBot...")

# Load card DB
try:
  with open('cards.json') as f:
    cards_db = json.load(f)
except:
  print("### ERROR! Unable to load cards.json, can not continue!")
  exit(1)

# Use settings in env variables 
# https://praw.readthedocs.io/en/latest/getting_started/configuration/environment_variables.html
reddit = praw.Reddit(user_agent='KeyForge Card Bot by /u/joyrexj9 1.0.0')
subreddit = reddit.subreddit(SUBREDDIT_NAME)
print("### Listening to new comments in /r/{}".format(SUBREDDIT_NAME))

def sigintHandler(sig, frame):
  print('### Closing...')
  exit(0)

signal.signal(signal.SIGINT, sigintHandler)

pattern = re.compile(r'\[\[(.*?)\]\]', flags=re.M|re.I)

for comment in subreddit.stream.comments(skip_existing=SKIP_OLD):
  if comment.author.name != "KeyForgeCardBot":
    matches = pattern.findall(comment.body)
    if matches:
      card_hits = 0
      reply = ""
      print("### {} - Processing comment {} by {}".format(datetime.fromtimestamp(comment.created_utc).strftime('%d-%m-%Y %H:%M'), comment.id, comment.author.name))
      for card_name in matches:
        try:
          card = cards_db[card_name.lower()] 
          print("### - Found card: {} ({})".format(card['card_title'], card['id']))
          url = card['front_image'] 
          reply += "- [{}]({}) ({}, {}, {})".format(card['card_title'], url, card['house'], card['rarity'], card['card_type']) + "\n"
          card_hits = card_hits + 1
        except:
          print("### ERROR! Card [{}] not found in DB".format(card_name.lower()))

      reply += "\n^I ^am ^a ^bot. ^Put ^[[cardname]] ^into ^your ^comment ^to ^call ^me"

      try:
        if card_hits > 0:
          print("### Sending reply...")
          comment.reply(reply)
          print("### OK!\n")
      except Exception as e:
        print("!!!", e)

