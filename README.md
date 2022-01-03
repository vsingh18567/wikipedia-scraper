# Part 1

## General Approach
Glassdoor.com structures their website in a way that makes this task challenging. There is no complete list of companies, however it is possible to search for companies by location. Therefore, using a [Countries API](https://restcountries.com), I searched for all available companies in every country, compiling the results into a database. Of course, there are lots of duplicates which were ignored. 

## Technical Execution
I used Python for this project, utilizing the `selenium` library for the webscraping, `sqlite` for storing the data, and `multiprocessing` to parallelize the process. 

Glassdoor requires you to login when landing on their home page, however if you directly jump to 'https://www.glassdoor.co.in/Reviews/index.htm' in incognito mode, this is not required. Therefore, Selenium's driver was set to incognito mode. Glassdoor also uses a lot of JavaScript which doesn't immediately load, therefore I set `driver.implicitly_wait(10)` to ensure that the driver waits for elements to load before erroring out. 

`sqlite` is used to store the data as inserting into a database is easily parallelizable. A database was chosen over another format (e.g. csv) because it scales well and has a primary key, which means that attempts to insert the same company twice (e.g. McDonald's in the US and McDonald's in India) are taken care of by catching `sqlite.IntegrityError`.

Lastly, because all the countries can be scraped individually, this process is parallelized using `multiprocessing`, which creates a thread pool such that upto 4 countries' webpages can be scraped concurrently. 

### Performance

Using my Macbook Pro, running `part1.py` scraped 7167 unique companies in 15 minutes at a rate of 8 companies/second. At this rate, it would take 52 hours to scrape all 1.5 million companies. However, given superior hardware (more cores, more RAM, better WiFi), this process can be finished much faster, especially if the number of threads is increased e.g.
```python
# part1.py, line 115
pool = Pool(processes=10) # if hardware has 10 cores
```

### Assumptions
1. Every company is listed in at least 1 country
    - Perhaps it is possible that a company is fully remote and doesn't appear on any country's page.
2.  The location of every company is included in the REST Countries API
    - Perhaps some companies have their location in a special territory that is not given by the API. 
3. The `data-emp-id` attribute on each div is the unique id for every company
    - It seems to be this way, but this is assumed.
