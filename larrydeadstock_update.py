
import sys
sys.path.append("C:\Sneaks4Sure\Scrapper\my_env\Lib\site-packages")
from datetime import date
from pymongo import MongoClient
import threading
from bs4 import BeautifulSoup
import requests
import json
import time
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW
import re
from currency_converter import CurrencyConverter
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from proxy import get_random_hdr, get_random_proxy


class LarryDeadStock:
    def __init__(self, url = None, stylId = None):
        self.url = ''
        self.stylId = ''

    def search_ByStyleId(self, stylId):
        # url = 'https://larrydeadstock.com/?s={}&post_type=product'.format(stylId)
        url = 'https://larrydeadstock.com/?s={}&post_type=product'.format("BD7399-28")
        while True:
            try:
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(url)
                time.sleep(5) 
                html = driver.page_source 
                # Now, we could simply apply bs4 to html variable 
                soup = BeautifulSoup(html, "html.parser") 
                if "This site can’t be reached" in soup.text:
                        proxy, chrome_options = get_random_proxy()
                        drive.close()
                        continue
                break
            except:
                proxy, chrome_options = get_random_proxy()
                driver.quit() 
        all_divs = soup.find('div', {'class' : 'woodmart-wishlist-btn wd-action-btn wd-wishlist-btn wd-style-text'})
        if all_divs is not None: 
            href_url = all_divs.find('a')
            product_url =  href_url['href']
        else:
            return None, None
        ul_tag = soup.find_all('ul', {'class':'list-unstyled sneakers'}) 
        price_size = []
        try:
            if ul_tag is not None: 
                for li_tag in ul_tag:
                    li_list = li_tag.find_all('li', {'class':'select-option choose_size_custom'})
                    if li_list is not None:
                        for span_tag in li_list:
                            field = span_tag.find('div', {'class':'inset'}).text
                            value = span_tag.get('id')
                            if '€' in value:
                                price = value.replace('€', '').strip()
                                price_size.append([field.strip(), price])
                driver.quit() # closing the webdriver 
                return price_size, product_url
            else:
                driver.quit() # closing the webdriver 
                return None, None
        except Exception as ex:
            driver.quit() # closing the webdriver 
            return None, None
        # driver.quit() # closing the webdriver 
   

class scraperThread_forLarry(threading.Thread):
     def __init__(self, _styleId):
         threading.Thread.__init__(self)
         self._styleId = _styleId
     def run(self):
         # Get lock to synchronize threads
         threadLock.acquire()
         thread_for_Larry(self._styleId)
         # Free lock to release next thread
         threadLock.release()


def thread_for_Larry(styleId):
    size_priceInfo, url = Larry.search_ByStyleId(styleId)
    if url is not None and size_priceInfo is not None:
        product_url = url
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Larry_url":product_url}})
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Larry_priceSize":size_priceInfo}})
        print("success of adding the price-size info from Larry")
    else:
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Larry_url":"-"}})
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Larry_priceSize":"-"}})
        print("product not exist in Larry")

def update_function(sku_id):
    thread_Larry = scraperThread_forLarry(sku_id)
    thread_Larry.start()
    thread_Larry.join()
    return "Finished Larry..."

if __name__ == "__main__":

    Larry = LarryDeadStock()
    c = CurrencyConverter()
    threadLock = threading.Lock()
    try: 
        conn = MongoClient() 
        print("Connected successfully!!!") 
    except:   
        print("Could not connect to MongoDB") 
    # sneaker_1 = Sneak()
    # database 
    db = conn.sneaks4sure 
    collection = db.Sneakers
    print("updating....")
    sku_id = sys.argv[1]
    update_function(sku_id)
    print("finished.....")
