import time
import argparse
import traceback
import csv
import os
import re
import sys
from glob import glob
from tqdm import tqdm
from base64 import b64encode
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
from urllib3.connectionpool import xrange

import geckodriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException

from scraper.setup_logger import ConsoleLogger


def do_login(driver, uname, pwd):

    # Define params for the scraper to hunt for
    login_url = "https://www.crunchbase.com/login"
    home_url = "https://www.crunchbase.com/home"  # Upon logging in successfully you'll be redirected here.
    profile_icon = "/html/body/chrome/div/app-header/div[1]/div[2]/div/logged-in-nav-row/nav-menu[3]/button/span[1]/nav-action-item-header-layout/div" #"layout-column layout-align-center-center cb-height-100 with-image ng-star-inserted"  # Class ID for something that exist post auth but not in the login page
    uname_id = "mat-input-1"  # Form ID for the username field.
    pwd_id = "mat-input-2"  # Form ID for the password field.

    try:
        # Go fetch the login page
        driver.get(login_url)
        # Find the login form
        uname_box = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, uname_id))
        )
        passwd_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, pwd_id))
        )
        # Fill in the form and login
        uname_box.click()
        uname_box.send_keys(uname)
        passwd_box.click()
        passwd_box.send_keys(pwd)
        passwd_box.send_keys(Keys.ENTER)
        # Now we want to wait and see if we logged in with the supplied username and password.
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(((By.XPATH, profile_icon)))
        )
        logger.debug(f"Sucessfully logged in with {uname}")

    except Exception as e:
        logger.error(f"Worker failed to login with {uname}: {e}")
        if vlevel >= 3:
            logger.spam(traceback.print_exc())
        driver.close()
        return False

    return True

def getDownLoadedFileName(driver, waitTime):
    """
    Get thefilename of the last downloaded file.
    :param driver: Firefox webdriver.
    :param waitTime: Number of seconds to wait maximum.
    :return: File Name of the file
    """
    driver.execute_script("window.open()")
    WebDriverWait(driver, 20).until(EC.new_window_is_opened)
    driver.switch_to.window(driver.window_handles[-1])
    driver.get("about:downloads")

    endTime = time.time()+waitTime
    while True:
        try:
            fileName = driver.execute_script("return document.querySelector('#contentAreaDownloadsView .downloadMainArea .downloadContainer description:nth-of-type(1)').value")
            if fileName:
                driver.close()
                driver.switch_to_window(driver.window_handles[0])
                return fileName
        except:
            pass
        time.sleep(1)
        if time.time() > endTime:
            break


def do_search(driver, search):

    search_url = "https://www.crunchbase.com/discover/acquisitions/"
    acquire_btn = "/html/body/chrome/div/mat-sidenav-container/mat-sidenav-content/div/discover/page-layout/div/div/div[2]/section[1]/div[1]/mat-accordion/mat-expansion-panel[3]/mat-expansion-panel-header/span/div/filter-group-header/div/mat-panel-title"  # Class of the "Acquiring Company" drop down button.
    acquirer_field = "mat-input-7"  # ID of the "Acquirer" search box.
    acquirer_popup = "mat-autocomplete-2"  # ID of the DIV for the pop up when you search for that company.
    export_button_xpath = "//*[contains(text(), 'Export to CSV')]"
    driver.get(search_url)

    try:
        ac_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, acquire_btn))
        )
        ac_btn.click()
        ac_searchbox = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, acquirer_field))
        )
        ac_searchbox.click()
        ac_searchbox.send_keys(search)
        # Wait for the menu to load fully before selecting it. Due to the way the menu is loaded a full sleep of the thread is best.
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, acquirer_popup))
        )
        time.sleep(3)

        ac_searchbox.send_keys(Keys.ARROW_DOWN)
        ac_searchbox.send_keys(Keys.ENTER)
        # Export the CSV.
        export_btn = driver.find_element_by_xpath(export_button_xpath)
        export_btn.click()

    except Exception as e:
        logger.error(f"Something went wrong on search {search}: {e}")
        if vlevel >= 3:
            logger.spam(traceback.print_exc())
        return False

    filename = getDownLoadedFileName(driver, 180)
    renamed_file = f'{download_dir}{search}_{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}.csv'
    os.rename(f"{download_dir}{filename}", renamed_file)

    logger.success(f"Successfully dumped results for {search} to {renamed_file}")
    return True


def setup_driver():

    fp = webdriver.FirefoxProfile()
    # Options for proxy.
    if http_proxy or https_proxy or socks_proxy:

        if proxy_uname:
            # Setup the login information if the proxy uses auth.
            credentials = f"{proxy_uname}:{proxy_pass}"
            credentials = b64encode(credentials.encode('utf-8')).decode('utf-8')
            fp.set_preference("extensions.closeproxyauth.authtoken", credentials)

        if http_proxy:
            proxy_host = http_proxy.split(":")[0]
            proxy_port = int(http_proxy.split(":")[1])
        if https_proxy:
            proxy_host = https_proxy.split(":")[0]
            proxy_port = int(https_proxy.split(":")[1])
        if socks_proxy:
            proxy_host = socks_proxy.split(":")[0]
            proxy_port = int(socks_proxy.split(":")[1])

        fp.set_preference("network.proxy.type", 1)
        fp.set_preference("network.proxy.http", proxy_host)
        fp.set_preference("network.proxy.http_port", proxy_port)
        fp.set_preference("network.proxy.https", proxy_host)
        fp.set_preference("network.proxy.https_port", proxy_port)
        fp.set_preference("network.proxy.ssl", proxy_host)
        fp.set_preference("network.proxy.ssl_port", proxy_port)
        fp.set_preference("network.proxy.ftp", proxy_host)
        fp.set_preference("network.proxy.ftp_port", proxy_port)
        fp.set_preference("network.proxy.socks", proxy_host)
        fp.set_preference("network.proxy.socks_port", proxy_port)

        fp.update_preferences()

    # Options for automatically downloading shit.
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", download_dir)
    fp.set_preference("browser.helperApps.neverAsk.openFile", "text/csv,text/plain,application/comma-separated-values,application/x-gzip,application/octet-stream")
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv,text/plain,application/comma-separated-values,application/x-gzip,application/octet-stream")
    fp.update_preferences()

    logger.debug(f"Setting up driver with: HTTP Proxy: {http_proxy}, SSL Proxy: {https_proxy}, SOCKS proxy: {socks_proxy}, Proxy Uname: {proxy_uname}, Proxy Pass: {proxy_pass}")
    driver = webdriver.Firefox(firefox_profile=fp)
    return driver


def run_worker(chunked_work):

    driver = setup_driver()
    logger.debug(f"Worker thread started, handling {len(chunked_work)}")
    login_status = do_login(driver, auth_uname, auth_pass)
    if login_status is False:
        logger.debug(f"Couldn't login for worker handling searches: {chunked_work}. Skipping...")
        return False
    for search in chunked_work:
        do_search(driver, search)
        pbar.update()

    logger.info(f"Worker has finished all {len(chunked_work)} searches.")
    driver.close()


def init_scraper():
    # Download and install geckodriver if it is not installed.
    geckodriver_autoinstaller.install()

    home = os.path.expanduser("~")
    scrapers_dir = "/Scrapers/"
    results_dir = "Crunchbase/"
    download_dir = f"{home}{scrapers_dir}{results_dir}"

    if os.path.exists(f"{home}{scrapers_dir}"):
        if os.path.exists(f"{home}{scrapers_dir}{results_dir}"):
            pass
        else:
            os.mkdir(f"{home}{scrapers_dir}{results_dir}")
    else:
        os.mkdir(f"{home}{scrapers_dir}")
        os.mkdir(f"{home}{scrapers_dir}{results_dir}")

    return download_dir


def shard(input_list, n):
    """ Yield successive n-sized chunks from an input list."""
    for i in xrange(0, len(input_list), n):
        yield input_list[i:i + n]


def find_ext(dr, ext):
    return glob(os.path.join(dr, f"*.{ext}"))


def parse_results():

    unique_domains = set()
    csv_files = find_ext(download_dir, 'csv')
    for fname in csv_files:
        with open(fname, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if parse_json:
                    if filters:
                        printable_row = {}
                        for filter in filters:
                            # --filters "Acquiree Name,Acquiree's Website,Acquirer Name,Acquirer's Website"
                            printable_row[filter] = row.get(filter)
                        print(printable_row)
                    else:
                        print(row)

                acquiree_website = row.get("Acquiree's Website")
                if acquiree_website:
                    domain = re.search('https?://([A-Za-z_0-9.-]+).*', acquiree_website)
                    unique_domains.add(domain.group(1))

    return unique_domains

def main():

    default_download_dir = init_scraper()

    parser = argparse.ArgumentParser('Based CrunchBase Scraper')
    # Switched args
    parser.add_argument("-v", dest="verbose", action='count', default=1,
                        help="Enable verbose output. Ex: -v, -vv, -vvv")
    parser.add_argument("-iL", "--input-list", dest="inlist", help="Input list of searches to perform")
    parser.add_argument("-s", "--search", dest="search", help="Perform a singular search on the 'Acquirer' filter.")
    parser.add_argument("-w", "--workers", dest="workers", default=12, help="Number of selenium workers to use. Default: 12")
    parser.add_argument("-d", "--download-dir", dest="download_dir", default=default_download_dir, help="Directory to download results to. Default: ~/Scrapers/Crunchbase/")
    parser.add_argument("--http-proxy", dest="http_proxy", default=None, help="HTTP Proxy for Selenium. Ex: 127.0.0.1:8080")
    parser.add_argument("--https-proxy", dest="https_proxy", default=None, help="HTTPS Proxy for Selenium. Ex: 127.0.0.1:8080")
    parser.add_argument("--socks-proxy", dest="socks_proxy", default=None, help="SOCKS Proxy for Selenium. Ex: 127.0.0.1:9050")
    parser.add_argument("--proxy-user", dest="proxy_uname", default=None, help="Username for proxy authentication.")
    parser.add_argument("--proxy-pass", dest="proxy_pass", default=None, help="Password for proxy authentication.")
    parser.add_argument("-u", "--user", dest="uname", help="Username to authenticate with.", required=True)
    parser.add_argument("-p", "--pass", dest="pwd", help="Password to authenticate with.", required=True)
    parser.add_argument("--parse", dest="parse_json", action="store_true", help="Parse all the results in the dumps dir to STDOUT as JSON. Filter by fieldnames with --filter.")
    parser.add_argument("--filters", dest="filters", help="Filter what fields are displayed when parsing. Ex: --filter \"Acquiree Name,Acquiree's Website,Acquirer Name,Acquirer's Website\"")
    parser.add_argument("--domainlist", dest="make_targlist", action="store_true", help="Parse only the domain names in the dumps dir to STDOUT. Automatically deduplicates")

    args = parser.parse_args()

    global vlevel
    vlevel = args.verbose
    global logger
    logger = ConsoleLogger(vlevel)
    global download_dir
    download_dir = args.download_dir
    global http_proxy
    http_proxy = args.http_proxy
    global https_proxy
    https_proxy = args.https_proxy
    global socks_proxy
    socks_proxy = args.socks_proxy
    global proxy_uname
    proxy_uname = args.proxy_uname
    global proxy_pass
    proxy_pass = args.proxy_pass
    global auth_uname
    auth_uname = args.uname
    global auth_pass
    auth_pass = args.pwd
    global pbar
    global workers
    workers = int(args.workers)
    global parse_json
    parse_json = args.parse_json
    global filters
    if args.filters:
        filters = args.filters.split(',')
    else:
        filters = None
    global make_targlist
    make_targlist = args.make_targlist

    if args.inlist:
        f = open(args.inlist, 'r')
        searches = list((l.rstrip("\n") for l in f))
    elif args.search:
        searches = [args.search]
    elif args.parse_json or args.make_targlist:
        domains = parse_results()
        if make_targlist:
            for domain in domains:
                print(domain)
        sys.exit(1)
    else:
        logger.error("Please specify either -s or -iL, or if just parsing specify one of the parsing options: --parse or --domainlist")
        sys.exit(1)

    pbar = tqdm(total=len(searches), unit=" searches", maxinterval=0.1, mininterval=0)

    chunk_size = int(len(searches)/workers)
    if chunk_size == 0:
        chunk_size = 1
    logger.spam(f"Using shard size: {chunk_size}")
    try:
        logger.info(f'Start time: {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}')
        p = Pool(workers)
        for _ in p.imap_unordered(run_worker, shard(searches, chunk_size)):
            pass
    except KeyboardInterrupt:
        pbar.close()
        logger.warning("Keyboard interrupt. Please wait, cleaning up...")
    finally:
        pbar.close()
        logger.info(f'End time: {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}')
        if args.parse:
            domains = parse_results()
            if make_targlist:
                for domain in domains:
                    print(domain)


if __name__ == "__main__":

    main()
