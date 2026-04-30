import downloader
import database

def auto_scrape():
    downloader.scrape_all()
    
def create_db():
    database.create()

def drop_db():
    database.drop()

def add_manga(url):
    database.add_entry(url)
    
def scrape_torrent(url):
    downloader.scrape_torrent(url)