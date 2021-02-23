# linkedin-jobs-scraper
> Scrape public available jobs on Linkedin using headless browser. 
> For each job, the following fields are extracted: `job_id`, `link`, `apply_link`, `title`, `company`, `place`, `description`, 
> `description_html`, `date`, `seniority_level`, `job_function`, `employment_type`, `industries`.

## Table of Contents

<!-- toc -->

* [Requirements](#requirements)
* [Installation](#installation)
* [Usage](#usage)
* [Anonymous vs authenticated session](#anonymous-vs-authenticated-session)
* [Rate limiting](#rate-limiting)
* [Proxy mode](#proxy-mode-experimental)
* [Filters](#filters)
* [Company filter](#company-filter)
* [Logging](#logging)
* [License](#license)

<!-- toc stop -->


## Requirements
- [Chrome](https://www.google.com/intl/en_us/chrome/) or [Chromium](https://www.chromium.org/getting-involved/download-chromium)
- [Chromedriver](https://chromedriver.chromium.org/)
- Python >= 3.6


## Installation
Install package:
```shell
pip install linkedin-jobs-scraper
```


## Usage 
```python
import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, ExperienceLevelFilters

# Change root logger level (default is WARN)
logging.basicConfig(level = logging.INFO)


def on_data(data: EventData):
    print('[ON_DATA]', data.title, data.company, data.date, data.link, len(data.description))


def on_error(error):
    print('[ON_ERROR]', error)


def on_end():
    print('[ON_END]')


scraper = LinkedinScraper(
    chrome_executable_path=None, # Custom Chrome executable path (e.g. /foo/bar/bin/chromedriver) 
    chrome_options=None,  # Custom Chrome options here
    headless=True,  # Overrides headless mode only if chrome_options is None
    max_workers=1,  # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
    slow_mo=1,  # Slow down the scraper to avoid 'Too many requests (429)' errors
)

# Add event listeners
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

queries = [
    Query(
        options=QueryOptions(
            optimize=True,  # Blocks requests for resources like images and stylesheet
            limit=27  # Limit the number of jobs to scrape
        )
    ),
    Query(
        query='Engineer',
        options=QueryOptions(
            locations=['United States'],
            optimize=False,
            limit=5,
            filters=QueryFilters(
                company_jobs_url='https://www.linkedin.com/jobs/search/?f_C=1441%2C17876832%2C791962%2C2374003%2C18950635%2C16140%2C10440912&geoId=92000000',  # Filter by companies
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.MONTH,
                type=[TypeFilters.FULL_TIME, TypeFilters.INTERNSHIP],
                experience=None,
            )
        )
    ),
]

scraper.run(queries)
```

## Anonymous vs authenticated session
By default the scraper will run in anonymous mode (no authentication required). In some environments (e.g. AWS or Heroku) 
this may be not possible though. You may face the following error message:

```
Scraper failed to run in anonymous mode, authentication may be necessary for this environment.
```

In that case the only option available is to run using an authenticated session. These are the steps required:
1. Login to LinkedIn using an account of your choice.
2. Open Chrome developer tools:

![](https://github.com/spinlud/py-linkedin-jobs-scraper/raw/master/images/img3.png)

3. Go to tab `Application`, then from left panel select `Storage` -> `Cookies` -> `https://www.linkedin.com`. In the
main view locate row with name `li_at` and copy content from the column `Value`.

![](https://github.com/spinlud/py-linkedin-jobs-scraper/raw/master/images/img4.png)

4. Set the environment variable `LI_AT_COOKIE` with the value obtained in step 3, then run your application as normal.
Example:

```shell script
LI_AT_COOKIE=<your li_at cookie value here> python your_app.py
```

## Rate limiting
You may experience the following rate limiting warning during execution: 
```
[429] Too many requests. You should probably increase scraper "slow_mo" value or reduce concurrency.
```

This means you are exceeding the number of requests per second allowed by the server (this is especially true when 
using authenticated sessions where the rate limits are much more strict). You can overcome this by:

- Trying a higher value for `slow_mo` parameter (this will slow down scraper execution). 
- Reducing the value of `max_workers` to limit concurrency. I recommend to use no more than one worker in authenticated
  mode.
- If you are using anonymous mode, you can try [proxy mode](#proxy-mode-experimental).  
  
## Proxy mode [experimental]
It is also possible to pass a list of proxies to the scraper:

```python
scraper = LinkedinScraper(
    chrome_executable_path=None,
    chrome_options=None,
    headless=True,
    max_workers=1,
    slow_mo=1,
    proxies=[
        'http://localhost:6666',
        'http://localhost:7777',        
    ]
)
```

**How it works?** Basically every request from the browser is intercepted and executed from a python library instead, using
one of the provided proxies in a round-robin fashion. The response is then returned back to the browser. In case of a proxy
error, the request will be executed from the browser (a warning will be logged to stdout).

**WARNING**: proxy mode is currently not supported when using an authenticated session.

## Filters
It is possible to customize queries with the following filters:
- RELEVANCE:
    * `RELEVANT`
    * `RECENT`
- TIME:
    * `DAY`
    * `WEEK`
    * `MONTH`
    * `ANY`
- TYPE:
    * `FULL_TIME`
    * `PART_TIME`
    * `TEMPORARY`
    * `CONTRACT`
- EXPERIENCE LEVEL:
    * `INTERNSHIP`
    * `ENTRY_LEVEL`
    * `ASSOCIATE`
    * `MID_SENIOR`
    * `DIRECTOR`
    
See the following example for more details:

```python
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, ExperienceLevelFilters


query = Query(
    query='Engineer',
    options=QueryOptions(
        locations=['United States'],
        optimize=False,
        limit=5,
        filters=QueryFilters(            
            relevance=RelevanceFilters.RECENT,
            time=TimeFilters.MONTH,
            type=[TypeFilters.FULL_TIME, TypeFilters.INTERNSHIP],
            experience=[ExperienceLevelFilters.INTERNSHIP, ExperienceLevelFilters.MID_SENIOR],
        )
    )
)
```

### Company Filter

It is also possible to filter by company using the public company jobs url on LinkedIn. To find this url you have to:
 1. Login to LinkedIn using an account of your choice.
 2. Go to the LinkedIn page of the company you are interested in (e.g. [https://www.linkedin.com/company/google](https://www.linkedin.com/company/google)).
 3. Click on `jobs` from the left menu.
 
 ![](https://github.com/spinlud/py-linkedin-jobs-scraper/raw/master/images/img1.png)

 
 4. Scroll down and locate `See all jobs` or `See jobs` button.
 
 ![](https://github.com/spinlud/py-linkedin-jobs-scraper/raw/master/images/img2.png)
 
 5. Right click and copy link address (or navigate the link and copy it from the address bar).
 6. Paste the link address in code as follows:
 
```python
query = Query(    
    options=QueryOptions(        
        filters=QueryFilters(
            # Paste link below
            company_jobs_url='https://www.linkedin.com/jobs/search/?f_C=1441%2C17876832%2C791962%2C2374003%2C18950635%2C16140%2C10440912&geoId=92000000',        
        )
    )
)
```
  
## Logging
Package logger can be retrieved using namespace `li:scraper`. Default level is `INFO`. 
It is possible to change logger level using environment variable `LOG_LEVEL` or in code:

```python
import logging

# Change root logger level (default is WARN)
logging.basicConfig(level = logging.DEBUG)

# Change package logger level
logging.getLogger('li:scraper').setLevel(logging.DEBUG)

# Optional: change level to other loggers
logging.getLogger('urllib3').setLevel(logging.WARN)
logging.getLogger('selenium').setLevel(logging.WARN)
```

## License
[MIT License](http://en.wikipedia.org/wiki/MIT_License)

If you like the project and want to contribute you can [donate something here](https://paypal.me/spinlud)!
