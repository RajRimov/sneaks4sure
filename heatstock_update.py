
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
from sneaks_model import Sneak
from pprint import pprint
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW
import re
from currency_converter import CurrencyConverter
from proxy import get_random_hdr, get_random_proxy



class HeatSneakers:
    def __init__(self, url = None, stylId = None):
        self.url = ''
        self.stylId = ''

    def search_ByStyleId(self, stylId):
        # url = 'https://heat-stock.com/search?q={}'.format("BV0072 001")
        url = 'https://heat-stock.com/search?q={}'.format(stylId)
        # proxy, chrome_options = get_random_proxy()
        #   # driver = webdriver.Chrome(options=chrome_options)
        # while True:
        #     try:
        #         driver = webdriver.Chrome(options=chrome_options)
        #         driver.get(url)
        #         time.sleep(5) 
        #         html = driver.page_source 
        #         # Now, we could simply apply bs4 to html variable 
        #         soup = BeautifulSoup(html, "html.parser") 
        #         if "This site can’t be reached" in soup.text:
        #                 proxy, chrome_options = get_random_proxy()
        #                 drive.close()
        #                 continue
        #         break
        #     except:
        #         proxy, chrome_options = get_random_proxy()
        #         driver.quit()
        options = Options()
        # options.add_argument('--headless')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36")
        while WebDriverException:
            try:
                driver = webdriver.Chrome('./chromedriver', chrome_options=options)
                driver.get(url)
                break
            except Exception as ex:
                print(ex)   
        time.sleep(5) 
        html = driver.page_source 
        # Now, we could simply apply bs4 to html variable 
        soup = BeautifulSoup(html, "html.parser")
        # time.sleep(5) 
        # html = driver.page_source 
        # soup = BeautifulSoup(html, "html.parser") 
        all_divs = soup.find('div', {'class' : 'grid__item small--one-half medium-up--one-fifth'})
        if all_divs is not None: 
            href_url = all_divs.find('a')
            driver.quit() # closing the webdriver 
            return "https://heat-stock.com" + href_url['href']
        else:
            driver.quit() # closing the webdriver 
            return None   
        # driver.quit() # closing the webdriver 
        

    def get_fromHeatSneakers(self, url):
        try:
            response = requests.get(url)
        except:
            return None
        # Now, we could simply apply bs4 to html variable 
        soup = BeautifulSoup(response.content, "html.parser") 
        select_content = soup.find('div', {'class' : 'selector-wrapper js product-form__item'})
        price_size = []
        try:
            if select_content is not None: 
                select = select_content.find('select')
                option_list = select.contents
                for each in option_list:
                    if each == ' ' or each  == '\n':
                        continue
                    str = each.text.split('-')
                    size  = re.findall(r'[-+]?\d*\.\d+|\d+', str[1])
                    if '€' in str[2]:
                        # res = re.findall(r'\d+', str[2])
                        # usd_value = c.convert(int(res[0]), 'EUR', 'USD')
                        price = str[2].replace('€', '').strip()
                        price_size.append([size[0], price])
                return price_size
            else:
                return None
        except Exception as ex:
            return None

class scraperThread_forHeatSneakers(threading.Thread):
    def __init__(self, _styleId):
        threading.Thread.__init__(self)
        self._styleId = _styleId
    def run(self):
        # Get lock to synchronize threads
        threadLock.acquire()
        thread_for_HeatSneakers(self._styleId)
        threadLock.release()


def thread_for_HeatSneakers(styleId):
    url = HeatSneakers_inst.search_ByStyleId(styleId)
    if url is not None:
        product_url = url
        size_priceInfo = HeatSneakers_inst.get_fromHeatSneakers(url)
        if size_priceInfo is not None:
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_HeatSneakers_priceSize":size_priceInfo}})
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_HeatSneakers_url":product_url}})
            print("success of scraping from HeatSneakers")
            
        else:
            print("product not exist in HeatSneakers")
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_HeatSneakers_url":product_url}})
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_HeatSneakers_priceSize":"-"}})
    else:
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_HeatSneakers_url":"-"}})
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_HeatSneakers_priceSize":"-"}})
        print("product not exist in HeatSneakers")

def thread_for_HeatSneakersByUrl(product_url, styleId):
    size_priceInfo = HeatSneakers_inst.get_fromHeatSneakers(product_url)
    if size_priceInfo is not None:
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_HeatSneakers_priceSize":size_priceInfo}})
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_HeatSneakers_url":product_url}})
        print("success of scraping from HeatSneakers")
        
    else:
        print("product not exist in HeatSneakers")
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_HeatSneakers_url":"-"}})
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_HeatSneakers_priceSize":"-"}})

def update_function(sku_id):
    thread_HeatSneakers = scraperThread_forHeatSneakers(sku_id)
    thread_HeatSneakers.start()
    thread_HeatSneakers.join()
    # thread_for_HeatSneakers(sku_id)
    return "Finished..."

if __name__ == "__main__":

    c = CurrencyConverter()
    HeatSneakers_inst = HeatSneakers()
    threadLock = threading.Lock()
    try: 
        conn = MongoClient() 
        print("Connected successfully!!!") 
    except:   
        print("Could not connect to MongoDB") 
    # database 
    db = conn.sneaks4sure 
    collection = db.Sneakers
    print("updating....")
    # brand = "asics"
    sku_id = sys.argv[1]
    # sku_id = "CD0461-046"
    cursor_list = collection.find({'product_sku_id': {'$regex':sku_id}})
    for product in cursor_list:
        if "product_HeatSneakers_url"  in product and "https://heat-stock.com/" in product['product_HeatSneakers_url']:
            product_url =  product['product_HeatSneakers_url']
            thread_for_HeatSneakersByUrl(product_url, sku_id)
        elif "product_HeatSneakers_url"  in product and "-" in product['product_HeatSneakers_url']:
            continue
        else:
            update_function(sku_id)
    print("finished.....")

