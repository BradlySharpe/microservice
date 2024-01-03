import requests
import os
import redis
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
import random
import concurrent.futures
import time
import json


ZIPRECUITER_ENDPOINT = os.environ['ENDPOINT_API']

REDIS_KEY = os.environ['REDIS_PORT']
REDIS_EXPIRY_SECONDS = os.environ['REDIS_EXPIRY_SECONDS']
REDIS_PORT = os.environ['REDIS_PORT'] or 6379

class ZipRecruiter:

    def __init__(self, logger):
        self.logger = logger
        self.logger.info("Init ZipRecruiter")
        parsed_url = urlparse(ZIPRECUITER_ENDPOINT)
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    def get_redis_client(self):
        try:
            self.logger.info("Getting redis client")
            return redis.StrictRedis(host="redis", port=REDIS_PORT, decode_responses=True)
        except Exception as e:
            self.logger.error("An error occurred while connecting to redis", e)
            return None

    def check_cache(self):
        self.logger.info("Checking cache")
        try:
            redis_client = self.get_redis_client()
            if redis_client is None:
                return None
            
            cached_json = redis_client.get(REDIS_KEY)
            redis_client.close()
            return json.loads(cached_json)
        except Exception as e:
            self.logger.error("An error occurred retreiving the cached jobs", e)
            return

    def set_cache(self, value):
        self.logger.info("Setting cache")
        try:
            redis_client = self.get_redis_client()
            if redis_client is None:
                return
            
            redis_client.setex(REDIS_KEY, REDIS_EXPIRY_SECONDS, json.dumps(value))
            redis_client.close()
        except Exception as e:
            self.logger.error("An error occurred while updating the cached jobs", e)

    def generate_random_user_agent(self):
        user_agents = [
            # Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            # Firefox
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            # Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            # Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.864.41 Safari/537.36 Edg/91.0.864.41",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.864.41 Safari/537.36 Edg/91.0.864.41",
            # Opera
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.203",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.203",
        ]

        return random.choice(user_agents)

    def get_headers(self):
        return {
            'User-Agent': self.generate_random_user_agent(),
            'Referer': 'https://www.ziprecruiter.com.au/',
            'Dnt': '1',
            'Cache-Control': 'max-age=0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.',
            'Accept-Language': 'en-US,en;q=0.9'
        }

    def get_next_pagination_url(self, soup: BeautifulSoup) -> str:
        pagination_div = soup.find('div', class_='jobs-pagination')
        if pagination_div is not None:
            inner_list = pagination_div.find('ul', class_='pagination')
            if inner_list is not None:
                last_li = inner_list.find_all('li')[-1]
                if last_li is not None:
                    if 'disabled' not in last_li.get('class', []):
                        last_a = last_li.find('a')
                        if last_a is not None:
                            return f"{self.base_url}{last_a.get('href')}"

        return None
    
    def get_job_body(self, url: str, retry = True) -> str:
        try:
            # Add delay to stagger requests
            # delay = random.uniform(0, 3)
            # time.sleep(delay)

            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            description = soup.find('div', class_='job-body')
            if description is not None:
                return description.get_text()
            
            description = soup.find('div', class_='job_description')
            if description is not None:
                inner_div = description.find('div')
                if inner_div is not None:
                    return inner_div.get_text()
                
                return description.get_text()

        except requests.exceptions.RequestException as e:
            if retry:
                return self.get_job_body(url, False)
        
        return None
    
    def parse_job_listing(self, listing: BeautifulSoup) -> object:
        if not listing.find('a'):
            return None
        
        title_element = listing.find('a', class_='jobList-title')
        title = title_element.get_text()
        url = title_element.get('href')

        meta = listing.find('ul', class_='jobList-introMeta').find_all('li')
        description = listing.find('div', class_='jobList-description').get_text()
        posting_date = listing.find('div', class_='jobList-date').get_text()

        if len(meta) < 2:
            return None

        if posting_date is not None:
            today = datetime.now()

            posting_date = datetime.strptime(posting_date, '%d %b').replace(year=today.year)

            if posting_date > today:
                posting_date -= relativedelta(years=1)

            gmt_timezone = pytz.timezone('GMT')
            posting_date = posting_date.replace(tzinfo=gmt_timezone)
        
        return {
            "url": url.strip(),
            "title": title.strip(),
            "company_name": meta[0].get_text().strip(),
            "company_location": meta[1].get_text().strip(),
            "short_description": description.strip(),
            "description": self.get_job_body(url, False),
            "posted": posting_date.strftime('%Y-%m-%d %H:%M:%S %Z')
        }

    def scrape_job_listings(self, url: str) -> list:
        self.logger.info(f"Scraping page: {url}")
        listings = []

        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            listings.extend(soup.find_all('li', class_='job-listing'))

            next_page_url = self.get_next_pagination_url(soup)
            if next_page_url:
                listings.extend(self.scrape_job_listings(next_page_url))

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching URL: {e}")
        
        return listings
    
    def scrape_jobs(self, url: str) -> list:
        self.logger.info(f"Scraping jobs")
        jobs = []

        job_listings = [listing for listing in self.scrape_job_listings(url) if listing is not None]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            jobs = list(executor.map(self.parse_job_listing, job_listings))

        return jobs

    def format_response(self, jobs, cached = True, update_cache = False):
        job_count = len(jobs) if jobs else 0
        job_type = "cached " if cached else ""

        self.logger.info(f"Got {job_count} {job_type}job(s)")

        if update_cache:
            self.set_cache(jobs)

        return {
            "jobs": jobs,
            "jobCount": job_count
        }

    def fetch_zip_recruiter_jobs(self, update_cache = True):    
        self.logger.info("Fetching jobs from Zip Recruiter")
        zipRecruiterJobs = self.scrape_jobs(ZIPRECUITER_ENDPOINT)

        return self.format_response(zipRecruiterJobs, False, update_cache)
    

    def get_jobs(self):
        self.logger.info("Fetching jobs")
        zipRecruiterJobs = self.check_cache()
        job_count = len(zipRecruiterJobs) if zipRecruiterJobs else 0

        if zipRecruiterJobs:
            return self.format_response(zipRecruiterJobs)
        
        return self.fetch_zip_recruiter_jobs()