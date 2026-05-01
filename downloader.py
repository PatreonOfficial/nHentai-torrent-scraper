'''
response from https://nhentai.net/api/v2/galleries?page=1&per_page=1
{
  "result": [
    {
      "id": 645834,
      "media_id": "3904166",
      "english_title": "[Sanbaizu] Hand*ob Nurse and the Ladies' Room",
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
from os import mkdir

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
        print("settings.json created, please set up!")
        exit()

def validize_url(url):
  if url.startswith("https://nhentai.net/g/") or url.startswith("nhentai.net/g/"):
    return "https://nhentai.net/g/" + url.split("/")[-1]
  elif url.isdigit():
    return "https://nhentai.net/g/" + url
  else:
    print("Invalid Url or ID")
    raise SystemExit(0)

def id_from_url(url):
  if url.startswith("https://nhentai.net/g/") or url.startswith("nhentai.net/g/"):
    return url.split("/")[-1]
  elif url.isdigit():
    return url
  else:
    print("Invalid Url or ID")
    raise SystemExit(0)

def scrape_all():
  r = requests.get('https://nhentai.net/api/v2/galleries?page=1&per_page=100', headers={"Authorization": apiKey})

  startFrom = 1 #currently at 6104
  for page in range(startFrom, (r.json()["num_pages"]+1)):
      r = requests.get(f'https://nhentai.net/api/v2/galleries?page={page}&per_page=100', headers={"Authorization": apiKey, "User-Agent":"nHentai scraper from github.com/patreonofficial"})
      if (r.status_code == 429): #page % 30 == 0
          print("waiting 20 seconds")
          sleep(20)
          r = requests.get(f'https://nhentai.net/api/v2/galleries?page={page}&per_page=100',
                          headers={"Authorization": apiKey})
      for manga in r.json()["result"]:
          db.add_entry(manga)

def scrape_one_url(url):
  validUrl = validize_url(url)
  
  result = requests.get(validUrl, headers={"Authorization": apiKey, "User-Agent":"nHentai scraper from github.com/patreonofficial"}).json()
  
  # convert single galerie in suitable format for add_entry
  tags = []
  for tag in result["tags"]:
    tags.append(tag["id"])
  
  manga = {
      "id": result["id"],
      "media_id": result["media_id"],
      "english_title": result["title"]["english"],
      "japanese_title": result["title"]["japanese"],
      "thumbnail": result["thumbnail"]["path"],
      "num_pages": result["num_pages"],
      "tag_ids": tags,
    }
  
  db.add_entry(manga)
  
  
# something takes long(5 sec delay added by nhentai)
# currently does not work
def scrape_torrent(url):
  validUrl = validize_url(url)
  id = id_from_url(validUrl)
  paddedId = id.rjust(6, '0')
  
  print("Downloading torrent for " + id)
  
  r = requests.post("https://nhentai.net/api/v2/galleries/" + id + "/download?format=torrent", headers={"Authorization": "Key " + apiKey, "User-Agent":"nHentai scraper from github.com/patreonofficial"})
  torrent = requests.get(r.json()["url"])
  
  print(torrent.content)
  
  folder = f"torrents/{paddedId[0]}{paddedId[1]}"
  
  try:
    mkdir(folder)
  except FileExistsError:
    pass
  open(f"{folder}/{paddedId}.torrent", 'wb').write(torrent.content)
  
  #add to db
  db.add_torrent_tag(id)
  
scrape_torrent("1")