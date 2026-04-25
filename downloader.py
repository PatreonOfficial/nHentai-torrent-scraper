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


apiKey = "Your key, not really nessasary"

r = requests.get('https://nhentai.net/api/v2/galleries?page=1&per_page=100', headers={"Authorization": apiKey})

startFrom = 1800 #currently at 1800
for page in range(startFrom, (r.json()["num_pages"])):
    print(page)
    r = requests.get(f'https://nhentai.net/api/v2/galleries?page={page}&per_page=100', headers={"Authorization": apiKey, "User-Agent":"nHentai scraper from github.com/patreonofficial"})
    if (page % 30 == 0  or r.status_code == 429):
        print("waiting 10 seconds")
        sleep(10)
        r = requests.get(f'https://nhentai.net/api/v2/galleries?page={page}&per_page=100',
                         headers={"Authorization": apiKey})
    for manga in r.json()["result"]:
        db.add_entry(manga)
