# Wikipedia Scraper

This scraper scrapes Wikipedia pages and for each page, it finds all related topics that are brought up in the opening paragraph. The data then gets stored in a MongoDB database. This sort of data could be used to build an assosciation graph / collect data for NLP work. In practice, it is impractical to use this scraper to scrape all of Wikipedia.

However, this project implements a useful DevOps infrastructure. The application is Dockerized and published to DockerHub. There is also a K8s manifest written that allows the scraper to be distributed so that Wikipedia pages can be scraped in parallel using replicas of the Docker image. This has been deployed to AWS EKS. 

The ideal number of replicas seems to be 8, after which performance does not seem to improve. 

![see performance.png](performance.png)

This is the final project for CIS 188 - DevOps. 