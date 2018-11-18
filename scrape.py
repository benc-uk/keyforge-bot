from urllib.request import Request, urlopen
from pprint import pprint
import json
import time

# Open existing cards files
try:
  with open('cards.json') as f:
    cards = json.load(f)
except:
  # Otherwise start with empty dict
  cards = dict()

# Fetch data from Keyforge API, note the &links=cards
for p in range(1, 20):
  url = "https://www.keyforgegame.com/api/decks/?page={}&page_size=500&ordering=-date&links=cards&lang=en".format(p)
  req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
  web_byte = urlopen(req).read()
  json_resp = web_byte.decode('utf-8')
  raw_data = json.loads(json_resp)

  # Loop over results and push into cards dict with card_title as key
  for card in raw_data['_linked']['cards']:
    if not card['is_maverick']:
      title = card['card_title']
      title = title.lower()
      title = title.replace("\u201c", "")
      title = title.replace("\u201d", "")
      title = title.replace("\u2019", "'")
      title = title.replace("\u00e6", "ae")

      # Brute force the card in even if it exists already, that's why we use a dict
      cards[title] = card
      #cards[card['id']] = card

  print("Total cards in DB: ", len(cards))
  if len(cards) == 370:
    break
  time.sleep(5)

# Save to cards.json
with open('cards.json', 'w+') as outfile:
  json.dump(cards, outfile, indent=2)