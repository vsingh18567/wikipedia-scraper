import requests
import pymongo
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import certifi
import random
import time

load_dotenv()    
db_username = os.getenv('MONGO_USERNAME')
db_password = os.getenv('MONGO_PASSWORD')
db_name = "CIS_188"
base_url = "https://www.glassdoor.co.in/Reviews/index.htm"
db_client = pymongo.MongoClient(f"mongodb+srv://{db_username}:{db_password}@cluster0.9jzwq.mongodb.net/{db_name}?retryWrites=true&w=majority",
    tlsCAFile=certifi.where())
db = db_client.get_database('CIS_188')

base_url = "https://en.wikipedia.org"
random_url = "https://en.wikipedia.org/wiki/Special:Random"

def query(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.content, "html.parser")
    name = soup.find(id="firstHeading")
    description = soup.find('p')
    links = description.findChildren("a", recursive=False)
    data = {
        "url": url,
        "name": name.text,
        "description": description.text,
        "links": []
    }
    tasks = []
    for link in links:
        link_url = base_url + link["href"]
        existing_doc = db["articles"].find_one({"url": link_url})
        if existing_doc == None:
            new_task = {
                "url": link_url
            }
            tasks.append(new_task)
        else:
            data["links"].append(existing_doc["_id"])
    new_article = db["articles"].insert_one(data)
    for task in tasks:
        task["from"] = new_article.inserted_id
        db["tasks"].insert_one(task)
    return new_article.inserted_id
        

def query_random():
    query(random_url)

def query_task(task):
    _id = query(task["url"])
    from_document = db["articles"].find_one({"_id": task["from"]})
    new_links = from_document["links"]
    new_links.append(_id)
    db["articles"].update_one({"_id": task["from"]}, {"$set": {"links": new_links}})
    db["tasks"].delete_one({"url": task["url"]})

count = 0

while count < (10 ** 6):
    try:
        num_tasks = db["tasks"].count_documents({})
        if num_tasks == 0:
            query_random()
        else:
            new_task = list(db["tasks"].aggregate([{ "$sample": { "size": 1 } }]))[0]
            query_task(new_task)    
        time.sleep(2)
        count += 1
    except:
        pass
