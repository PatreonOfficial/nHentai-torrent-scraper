import sqlite3 as db
import json
import requests
import time

with open('settings.json') as file:
        d = json.load(file)["website"]
        apiKey = d["api-key"]

connection = db.connect("database.db")
cursor = connection.cursor()

# create nHentai db
def create():
    try:

        sql = """CREATE TABLE mangas (
        id int PRIMARY KEY,
        media_id int,
        title_english varchar(1024),
        title_japanese varchar(1024),
        thumbnail varchar(255),
        num_pages int
        )"""
        cursor.execute(sql)

        sql = """CREATE TABLE tagsId (
        id int,
        tag int not null,
        FOREIGN KEY (id)
        REFERENCES mangas(id)
        )"""

        cursor.execute(sql)
        sql = """CREATE TABLE tagNames (
                        tag_id int PRIMARY KEY,
                        tag_name varchar(1024),
                        tag_type varchar(1024),
                        tag_slug varchar(1024),
                        tag_url varchar(1024)
                        )"""
        cursor.execute(sql)
    except db.OperationalError:
        print("Database Allready set up")
        print("Use 'DROP nHentai' to drop db")

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()

def drop():
    if input("Are you sure? Y/N") != "Y" or "y":
        exit()
    if input("Are you really sure?\n this is going to drop the whole DB! Y/N") != "Y" or "y":
        exit()

    try:
        # Drops Database
        sql = "DROP DATABASE nHentai"
        cursor.execute(sql)
    except():
        print("Database exists")

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()

# Adds mangas to db
dquote = "\""
bslash = "\\"
def add_entry(manga):
    try:
        sql = f"""
        INSERT INTO mangas   (id, media_id, title_english, title_japanese, thumbnail, num_pages)
        VALUES              ({manga['id']}, {manga['media_id']}, \"{str(manga['english_title']).replace(dquote, dquote*2)}\", \"{str(manga['japanese_title']).replace(dquote, dquote*2)}\", \"{manga['thumbnail']}\", {manga['num_pages']}) 
        """
        print(sql)
        cursor.execute(sql)
        # add tags:
        sql = ""
        for tag in manga["tag_ids"]:
            sql = f"INSERT INTO tagsId (id, tag) VALUES ({manga['id']}, {tag})"
            cursor.execute(sql)
        connection.commit()

    except(db.IntegrityError):
        print(f"Entry with id {manga['id']} exists")
    except(db.InterfaceError):
        print("db.err.InterfaceError")

def match_tags():
    

    # to copy tag ids
    #INSERT INTO tagNames (tag_id) SELECT DISTINCT tag FROM tagsId;
    #select tag_id from tagNames where tag_name IS NULL limit 100;
    
    # Example tag
    # {
    #     "id": 1,
    #     "type": "group",
    #     "name": "mu-keikaku",
    #     "slug": "mu-keikaku",
    #     "url": "/group/mu-keikaku/",
    #     "count": 12
    #  }
    
    while True:
        startTime = time.time()
        for n in range(14):
            
            #api referance:
            # https://nhentai.net/api/v2/tags/ids?ids=54%2C58
            url = "https://nhentai.net/api/v2/tags/ids?ids="
            
            sql = "select tag_id from tagNames where tag_name IS NULL limit 100;"
            cursor.execute(sql)
            result = cursor.fetchall()
            
            if result.__len__() == 0:
                print("Done with tag meta data import")
                break
            
            for id in result:
                url += str(id[0]) + "%2c"
            r = requests.get(url, headers={"Authorization": apiKey})
            for tag in r.json():
                sql = f"""
                        UPDATE tagNames
                        SET tag_name = "{tag["name"]}", tag_type = "{tag["type"]}", tag_slug = "{tag["slug"]}", tag_url = "{tag["url"]}"
                        WHERE tag_id = {tag["id"]}
                        """
                cursor.execute(sql)
            connection.commit()
        endTime = time.time()
        
        
        wait = round(62-(endTime - startTime))
        for left in reversed(range(1, wait)):
            print(f"Waiting {left:2} seconds for Rate Limit", end='\r')
            time.sleep(1)
    
match_tags()