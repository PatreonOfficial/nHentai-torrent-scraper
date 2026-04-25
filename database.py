import pymysql
import json

#load settings
with open('settings.json') as file:
    d = json.load(file)["database"]
    host = d["host"]
    user = d["user"]
    password = d["pass"]
    db = d["db"]


connection = pymysql.connect(host=host,
                             user=user,
                             password=password,
                             database=db,
                             cursorclass=pymysql.cursors.DictCursor)

# create nHentai db
def create():
    with connection:
        with connection.cursor() as cursor:
            try:
                # Create a new record
                sql = "CREATE DATABASE nHentai"
                cursor.execute(sql)


                #add tables
                sql = "use nHentai"
                cursor.execute(sql)

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
                sql = """CREATE TABLE tagsName (
                                tag_id int PRIMARY KEY,
                                tag_name varchar(1024) not null
                                )"""
                cursor.execute(sql)
            except(pymysql.err.OperationalError):
                print("Database Allready set up")
                print("Use 'DROP nHentai' to drop db")

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()

def drop():
    with connection:
        with connection.cursor() as cursor:
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
    connection = pymysql.connect(host=host,
                                 user=user,
                                 password=password,
                                 database=db,
                                 cursorclass=pymysql.cursors.DictCursor)
    #print(manga["id"])
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("use nHentai")
            try:
                sql = f"""
                INSERT INTO mangas   (id, media_id, title_english, title_japanese, thumbnail, num_pages)
                VALUES              ({manga['id']}, {manga['media_id']}, \"{str(manga['english_title']).replace(dquote, bslash + dquote)}\", \"{str(manga['japanese_title']).replace(dquote, bslash + dquote)}\", \"{manga['thumbnail']}\", {manga['num_pages']}) 
                """
                cursor.execute(sql)
                # add tags:
                sql = ""
                for tag in manga["tag_ids"]:
                    sql = f"INSERT INTO tagsId (id, tag) VALUES ({manga['id']}, {tag})"
                    cursor.execute(sql)
                connection.commit()

            except(pymysql.err.IntegrityError):
                print(f"Entry with id {manga['id']} exists")
            except(pymysql.err.InterfaceError):
                print("pymysql.err.InterfaceError")

def match_Tags():
    pass