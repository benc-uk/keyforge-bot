#!/usr/bin/python3
 
import praw
import re
import urllib
import sqlite3
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv
from pprint import pprint

DB_NAME        = '/data/replies.db'
SUBREDDIT_NAME = 'testingground4bots'
CARD_SITE_URL  = "http://aembertree.com/search?q={}"
SKIP_OLD       = True

print("### Starting KeyForgeCardBot...")

# Start up and config stuff
load_dotenv()

# Use settings in env variables https://praw.readthedocs.io/en/latest/getting_started/configuration/environment_variables.html
reddit = praw.Reddit()
subreddit = reddit.subreddit(SUBREDDIT_NAME)
print("### Listening to new comments in /r/{}".format(SUBREDDIT_NAME))

dbconn = sqlite3.connect(DB_NAME)
dbconn.cursor().execute('CREATE TABLE IF NOT EXISTS replied_to (comment_id text)')

def checkAlreadyReplied(id):
  cur = dbconn.cursor()
  cur.execute("SELECT COUNT(*) FROM replied_to WHERE comment_id = ?", [id])
  return cur.fetchone()[0] > 0

def saveReply(id):
  dbconn.cursor().execute("INSERT INTO replied_to VALUES (?)", [id])
  dbconn.commit()

def sigintHandler(sig, frame):
  print('### Closing...')
  dbconn.close()
  sys.exit(0)

signal.signal(signal.SIGINT, sigintHandler)

pattern = re.compile(r'\[\[(.*?)\]\]', flags=re.M|re.I)

for comment in subreddit.stream.comments(skip_existing=SKIP_OLD):
  if not checkAlreadyReplied(comment.id) and comment.author.name != "KeyForgeCardBot":
    matches = pattern.findall(comment.body)
    if matches:
      reply = ""
      print("### {} - Processing comment {} by {}".format(datetime.fromtimestamp(comment.created_utc).strftime('%d-%m-%Y %H:%M'), comment.id, comment.author.name))
      for card_name in matches:
        card_name_encoded = urllib.parse.quote_plus(card_name)
        url = CARD_SITE_URL.format(card_name_encoded)
        reply += "- [{}]({})".format(card_name, url) + "\n"

      reply += "\n^I ^am ^a ^bot. ^Put ^[[cardname]] ^into ^your ^comment ^to ^call ^me"

      try:
        print("### Sending reply...")
        comment.reply(reply)
        saveReply(comment.id)
        print("### OK!\n")
      except Exception as e:
        print("!!!", e)

