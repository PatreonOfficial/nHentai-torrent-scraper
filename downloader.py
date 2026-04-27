'''
response from https://nhentai.net/api/v2/galleries?page=1&per_page=1
{
  "result": [
    {
      "id": 645834,
      "media_id": "3904166",
      "english_title": "[Sanbaizu] Handjob Nurse and the Ladies' Room",
      "japanese_title": "[Sanbaizu] 手コキナースと女子便所",
      "thumbnail": "galleries/3904166/thumb.webp",
      "thumbnail_width": 250,
      "thumbnail_height": 334,
      "num_pages": 21,
      "tag_ids": [
        33172,
        8328,
        6346,
        2820
      ],
      "blacklisted": false
    }
  ],
  "num_pages": 610133,
  "per_page": 1,
  "total": 610095
'''

import database as db
import requests
from time import sleep
import json

#load settings
try:
    with open('settings.json') as file:
        d = json.load(file)["website"]
        apiKey = d["api-key"]
except FileNotFoundError:
    with open('settings.json', "x") as file:
        file.write("""{
  "website": {
    "api-key": "YourNHentaiApiKey"
  }
}
        """)
        print("settings.json created, pleas set up!")
        exit()



r = requests.get('https://nhentai.net/api/v2/galleries?page=1&per_page=100', headers={"Authorization": apiKey})

startFrom = 1 #currently at 6104
for page in range(startFrom, (r.json()["num_pages"]+1)):
    print(page)
    r = requests.get(f'https://nhentai.net/api/v2/galleries?page={page}&per_page=100', headers={"Authorization": apiKey, "User-Agent":"nHentai scraper from github.com/patreonofficial"})
    if (r.status_code == 429): #page % 30 == 0
        print("waiting 20 seconds")
        sleep(20)
        r = requests.get(f'https://nhentai.net/api/v2/galleries?page={page}&per_page=100',
                         headers={"Authorization": apiKey})
    for manga in r.json()["result"]:
        db.add_entry(manga)
