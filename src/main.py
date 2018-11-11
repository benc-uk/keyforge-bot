#!/usr/bin/python3
 
import praw
import os
import re
import urllib
import sqlite3
from dotenv import load_dotenv
from pprint import pprint

DB_NAME = 'replies.db'
SUBREDDIT_NAME = 'testingground4bots'
CARD_SITE_URL = "http://aembertree.com/search?q={}"

print("### Starting KeyForgeCardBot...")

# Start up and config stuff
load_dotenv()

# Use settings in env variables https://praw.readthedocs.io/en/latest/getting_started/configuration/environment_variables.html
reddit = praw.Reddit()
subreddit = reddit.subreddit(SUBREDDIT_NAME)
print("### Listening to new comments in /r/{}".format(SUBREDDIT_NAME))

dbconn = sqlite3.connect(DB_NAME)
dbconn.cursor().execute('CREATE TABLE IF NOT EXISTS replied_to (comment_id text)')

def commentReplied(id):
  cur = dbconn.cursor()
  cur.execute("SELECT COUNT(*) FROM replied_to WHERE comment_id = ?", [id])
  return (cur.fetchone()[0] > 0)

def saveReply(id):
  dbconn.cursor().execute("INSERT INTO replied_to VALUES (?)", [id])
  dbconn.commit()

pattern = re.compile(r'\[\[(.*?)\]\]', flags=re.M|re.I)

for comment in subreddit.stream.comments():
  if not commentReplied(comment.id) and comment.author.name != "KeyForgeCardBot":
    matches = pattern.findall(comment.body)
    if matches:
      reply = ""
      for card_name in matches:
        card_name_encoded = urllib.parse.quote_plus(card_name)
        url = CARD_SITE_URL.format(card_name_encoded)
        reply += "- [{}]({})".format(card_name, url) + "\n"

      print("### Made a reply\n", reply)
      reply += "\n^I ^am ^a ^bot. ^Put ^[[cardname]] ^into ^your ^comment ^to ^call ^me"

      try:
        print("### Sending reply...")
        comment.reply(reply)
        saveReply(comment.id)
        print("### OK!\n")
      except Exception as e:
        print(e)

