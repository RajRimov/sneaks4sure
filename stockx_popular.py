import sys
sys.path.append("C:\Sneaks4Sure\Scrapper\my_env\Lib\site-packages")
from datetime import date
from pymongo import MongoClient
import threading
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from currency_converter import CurrencyConverter
from selenium import webdriver 
import requests
import re
import time
from proxy import get_random_hdr, get_random_proxy,get_random_proxy_forGoat


def get_product_url(url):
    chrome_options = webdriver.ChromeOptions()
    proxy= get_random_proxy_forGoat()
    chrome_options.add_argument('--proxy-server=%s' % proxy)
    while True:
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            time.sleep(5) 
            html = driver.page_source 
            # Now, we could simply apply bs4 to html variable 
            soup = BeautifulSoup(html, "html.parser") 
            if "This site can’t be reached" in soup.text or "Attention Required!" in soup.text or "This page isn’t working" in soup.text or soup.text == '':
                proxy = get_random_proxy_forGoat()
                chrome_options.add_argument('--proxy-server=%s' % proxy)
                driver.quit()
                continue
            break
        except:
            proxy = get_random_proxy_forGoat()
            chrome_options.add_argument('--proxy-server=%s' % proxy)
            pass
    all_divs = soup.find('div', {'class' : 'browse-grid'})
    url_list = []
    if all_divs is not None: 
        product_div = all_divs.find_all('div', {'class' : 'tile browse-tile'})
        for product in product_div:
            href_url = product.find('a')
            product_url = "https://stockx.com" + href_url['href']
            url_list.append(product_url)
        driver.quit() # closing the webdriver 
        return url_list
    else:
        driver.quit() # closing the webdriver 
        return None   

def Diff(li1, li2):
    return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))

def store_popular_db(new_popular_list, prior_popular_list, total_list):
    # get the url list which not exist in prior popular list.
    real_newUrl_list = Diff(new_popular_list, prior_popular_list)
    for each_NewURL in real_newUrl_list:
        if each_NewURL in total_list:
            # get the product info from totalSneakers collection
            cursor_list = collection_total.find({'product_stock_url': {'$regex':each_NewURL}})
            for product in cursor_list:
                # add the new product in sneakers collection
                try:
                    collection.insert(product)
                except Exception as ex:
                    print(ex)
                    continue
        else:
            continue


if __name__ == "__main__":
    
    # flag for updating the scraped data.
    try: 
        conn = MongoClient() 
        print("Connected successfully!!!") 
    except:   
        print("Could not connect to MongoDB") 
    # database 
    db = conn.sneaks4sure 

    # get the url list from prior sneakers
    collection = db.Sneakers
    prior_popular_list = []
    cursor_prior_list = collection.find({})
    for product in cursor_prior_list:
        prior_popular_list.append(product['product_stock_url'])
    
    # get the url list from total sneakers.
    total_list = []
    collection_total = db.TotalSneakers
    cursor_total_list = collection_total.find({})
    for product in cursor_total_list:
        total_list.append(product['product_stock_url'])

    # get the url list of new popular products
    new_popular_list = []
    # for 25 pages
    start_time = time.time()
    for index in range(25):
        popular_product_url = "https://stockx.com/sneakers/most-popular?page={}".format(index + 1)
        page_product_list = get_product_url(popular_product_url)
        if page_product_list is not None:
            new_popular_list.extend(page_product_list)
            print("success in getting product urls in page {}".format(index + 1))
        else:
            print("Fail in getting product urls in page {}".format(index + 1))
    store_popular_db(new_popular_list, prior_popular_list, total_list)
    total_time = time.time() - start_time
    print("--- %s seconds ---" % (time.time() - start_time))
    sys.exit(0)