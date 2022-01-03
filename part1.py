from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import requests
from multiprocessing import Pool
import time
import sqlite3

# set up database
conn = sqlite3.connect("data.db")
delete_table_sql = "DROP TABLE data"
create_table_sql = """
CREATE TABLE IF NOT EXISTS data (
    id integer PRIMARY KEY,
    name text NOT NULL
)
"""
c = conn.cursor()
try:
    c.execute(delete_table_sql)
except sqlite3.OperationalError:
    pass
c.execute(create_table_sql)

# set up selenium
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--incognito")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
s = Service(ChromeDriverManager().install())

base_url = "https://www.glassdoor.co.in/Reviews/index.htm"


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


def scrape_page(driver):
    """
    Scrapes a particular page of companies

    driver: the Chrome driver being used

    returns: the element representing the button that is clicked to go to the next page
    """

    results = driver.find_elements(By.CLASS_NAME, "single-company-result")
    for result in results:
        id = result.get_attribute("data-emp-id")
        company = result.find_element(By.TAG_NAME, "h2").text
        insert_company(id, company)

    next_btn = driver.find_element(By.CLASS_NAME, "next")
    return next_btn


def parse(country):
    """
    Scrapes all the companies from a particular country

    country: country to parse

    returns: None
    """

    driver = webdriver.Chrome(service=s, options=options)
    driver.implicitly_wait(10)
    driver.get(base_url)

    # search for country
    el = driver.find_element(By.ID, "LocationSearch")
    el.send_keys(country)
    driver.find_element(By.ID, "HeroSearchButton").click()

    next_btn = scrape_page(driver)

    print(f"Page 1 from {country} complete")

    count = 1

    # while the next button is an <a> tag instead of a <span> tag
    # (i.e. while the next page exists)
    while len(next_btn.find_elements(By.TAG_NAME, "a")) > 0:
        start = time.time()
        # go to next page
        next_btn.click()
        next_btn = scrape_page(driver)
        end = time.time()
        count += 1
        print(f"Page {count} from {country} complete in {end - start}")


def set_up_threads(countries):
    """
    Creates a thread pool to parallelize the scraping by country

    countries: An iterable of names of countries
    """

    pool = Pool(processes=4)
    pool.map(parse, countries)


if __name__ == "__main__":
    countries = requests.get("https://restcountries.com/v3.1/all").json()
    countries = [country["name"]["common"] for country in countries]
    set_up_threads(countries)
    conn.close()
