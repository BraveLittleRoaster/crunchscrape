## Installation

!! Before running, make sure you have Selenium webdriver for Firefox installed and added to PATH !!
This code will automatically do this for you if you don't have it already.

Install with `python3 setup.py install`

## Configuration
Before running the scraper you should setup what columns you want to have exported. I'd just go ahead and check all of them.
Crunchbase saves your view on your account. For example, if you want to see Deal Info >> Price, you can login and check the box and then check "apply changes". 
Upon next login, all sessions will have that column available to export. 

1. Login to your account and navigate [here](https://www.crunchbase.com/discover/acquisitions/)
2. Click "Edit View"
3. Select what columns you want the scraper to automate exporting and click "Apply Changes"

![Instructions](https://imgur.com/RPW82zk)

Once you've done this you'll be set to run the scraper.

## Usage

```
usage: Based CrunchBase Scraper [-h] [-v] [-iL INLIST] [-s SEARCH] [-w WORKERS] [-d DOWNLOAD_DIR] [--http-proxy HTTP_PROXY] [--https-proxy HTTPS_PROXY] [--socks-proxy SOCKS_PROXY]
                                [--proxy-user PROXY_UNAME] [--proxy-pass PROXY_PASS] -u UNAME -p PWD [--parse] [--filters FILTERS] [--domainlist]

optional arguments:
  -h, --help            show this help message and exit
  -v                    Enable verbose output. Ex: -v, -vv, -vvv
  -iL INLIST, --input-list INLIST
                        Input list of searches to perform
  -s SEARCH, --search SEARCH
                        Perform a singular search on the 'Acquirer' filter.
  -w WORKERS, --workers WORKERS
                        Number of selenium workers to use. Default: 12
  -d DOWNLOAD_DIR, --download-dir DOWNLOAD_DIR
                        Directory to download results to. Default: ~/Scrapers/Crunchbase/
  --http-proxy HTTP_PROXY
                        HTTP Proxy for Selenium. Ex: 127.0.0.1:8080
  --https-proxy HTTPS_PROXY
                        HTTPS Proxy for Selenium. Ex: 127.0.0.1:8080
  --socks-proxy SOCKS_PROXY
                        SOCKS Proxy for Selenium. Ex: 127.0.0.1:9050
  --proxy-user PROXY_UNAME
                        Username for proxy authentication.
  --proxy-pass PROXY_PASS
                        Password for proxy authentication.
  -u UNAME, --user UNAME
                        Username to authenticate with.
  -p PWD, --pass PWD    Password to authenticate with.
  --parse               Parse all the results in the dumps dir to STDOUT as JSON. Filter by fieldnames with --filter.
  --filters FILTERS     Filter what fields are displayed when parsing. Ex: --filter "Acquiree Name,Acquiree's Website,Acquirer Name,Acquirer's Website"
  --domainlist          Parse only the domain names in the dumps dir to STDOUT. Automatically deduplicates
```

Example: `basedcrunch -s Microsoft -u bill.gates@microsoft.com -p 'VaccinesCauseAutism123!' -vvv --parse --filters "Acquiree Name,Acquiree's Website,Acquirer Name,Acquirer's Website"`

Filterable fields:

- Transaction Name
- Transaction Name URL
- Acquiree Name
- Acquiree Name URL
- Announced Date
- Announced Date Precision
- Acquirer Name
- Acquirer Name URL
- Acquirer's Website
- Acquirer Headquarters Location
- Acquiree's Website
- Price
- Price Currency
- Price Currency (in USD)
- Acquisition Type
- Acquisition Terms
- Acquiree's Number of Funding Rounds
- Acquiree Funding Status
- Acquiree's Total Funding Amount
- Acquiree's Total Funding Amount Currency
- Acquiree's Total Funding Amount Currency (in USD)
- Acquiree's Estimated Revenue Range
- Acquiree Headquarters Location
- Acquiree Last Funding Type
- Acquiree Description
- Acquiree Industries
- CB Rank (Acquisition)
- Acquirer's Description
- Acquirer Industries
- Acquirer's Estimated Revenue Range
- Acquirer's Total Funding Amount
- Acquirer's Total Funding Amount Currency
- Acquirer's Total Funding Amount Currency (in USD)
- Acquirer's Number of Funding Rounds
- Acquirer Funding Status
