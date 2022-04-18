from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import requests
from multiprocessing import Pool, cpu_count
import time
import sqlite3
from dotenv import load_dotenv
import pymongo
import os
import certifi
import random






# set up selenium
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--incognito")
options.add_argument("--no-sandbox")
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
s = Service(ChromeDriverManager().install())


def insert_company(id, name):
    """
    Inserts a company into the database
    """

    sql = "INSERT INTO data (id, name) VALUES (?, ?)"
    c = conn.cursor()
    try:
        c.execute(sql, [id, name])
    except sqlite3.IntegrityError:  # duplicate company
        pass
    conn.commit()


def scrape_page(driver, db):
    """
    Scrapes a particular page of companies

    driver: the Chrome driver being used

    returns: the element representing the button that is clicked to go to the next page
    """

    results = driver.find_elements(By.CLASS_NAME, "single-company-result")
    data = []
    for result in results:
        id = result.get_attribute("data-emp-id")
        company = result.find_element(By.TAG_NAME, "h2")
        company_name = company.find_element(By.TAG_NAME, "a").text
        print(id, company_name)
        data.append({
            "_id": id,
            "company": company_name
        })
        try:
            db.companies.insert_one({"_id": id, "company": company_name})
        except pymongo.errors.DuplicateKeyError:
            pass

    # res = db.companies.insert_many(data, ordered=False)
    next_btn = driver.find_element(By.CLASS_NAME, "next")
    return next_btn


def parse(country, db):
    """
    Scrapes all the companies from a particular country

    country: country to parse

    returns: None
    """
    

    driver = webdriver.Chrome(service=s, options=options)
    driver.implicitly_wait(10)
    driver.get(base_url)

    if db.countries.find_one({"name": country}) != None:
        return
    db.countries.insert_one({"name": country})

    # search for country
    el = driver.find_element(By.ID, "LocationSearch")
    el.clear()
    el.send_keys(country)
    driver.find_element(By.ID, "HeroSearchButton").click()

    next_btn = scrape_page(driver, db)

    print(f"Page 1 from {country} complete")

    count = 1

    # while the next button is an <a> tag instead of a <span> tag
    # (i.e. while the next page exists)
    while len(next_btn.find_elements(By.TAG_NAME, "a")) > 0:
        start = time.time()
        # go to next page
        next_btn.click()
        next_btn = scrape_page(driver, db)
        end = time.time()
        count += 1
        print(f"Page {count} from {country} complete in {end - start}")


def set_up_threads(countries):
    """
    Creates a thread pool to parallelize the scraping by country

    countries: An iterable of names of countries
    """

    pool = Pool(processes=cpu_count())
    pool.map(parse, countries)


if __name__ == "__main__":
    load_dotenv()    
    db_username = os.getenv('MONGO_USERNAME')
    db_password = os.getenv('MONGO_PASSWORD')
    db_name = "CIS_188"
    base_url = "https://www.glassdoor.co.in/Reviews/index.htm"

    db_client = pymongo.MongoClient(f"mongodb+srv://{db_username}:{db_password}@cluster0.9jzwq.mongodb.net/{db_name}?retryWrites=true&w=majority",
        tlsCAFile=certifi.where())
    db = db_client.get_database('CIS_188')

    countries = requests.get("https://restcountries.com/v3.1/all").json()
    # convert json to list of common country names
    countries = [country["name"]["common"] for country in countries]
    random.shuffle(countries)
    for country in countries:
        parse(country, db)
    # set_up_threads(countries)
