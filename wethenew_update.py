import sys
sys.path.append("C:\Sneaks4Sure\Scrapper\my_env\Lib\site-packages")
from datetime import date
from pymongo import MongoClient
import threading
import lxml
import lxml.html
from bs4 import BeautifulSoup
import requests
import json
import time
from selenium import webdriver 
import re
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from proxy import get_random_hdr, get_random_proxy

#check if the new styleId already exists in database
def alreadyExists(new_skuId):
     if collection.find({'product_sku_id': new_skuId}).count() > 0:
         return True
     else:
         return False

#get the styleId from database
def get_styleId_fromDB():
    query = {'product_sku_id': {'$exists': 1}}
    projection = {'_id': 0, 'product_sku_id': 1}

    data = list(collection.find(query, projection))

    skuId_list = []
    for sku_id in data:
        skuId_list.append(sku_id['product_sku_id'])
    return skuId_list

#get the styleId from database
def get_styleId_fromDB():
    query = {'product_sku_id': {'$exists': 1}}
    projection = {'_id': 0, 'product_sku_id': 1}

    data = list(collection.find(query, projection))

    skuId_list = []
    for sku_id in data:
        skuId_list.append(sku_id['product_sku_id'])
    return skuId_list

class Withenew:
    def __init__(self, url = None, stylId = None):
        self.url = ''
        self.stylId = ''

    def search_ByStyleId(self, stylId):
        url = 'https://wethenew.com/search?type=product&q={}*'.format(stylId)
        # url = 'https://wethenew.com/search?type=product&q={}*'.format("GY7924")
        # proxy, chrome_options = get_random_proxy()
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
        all_divs = soup.find('div', {'class' : 'container main content'})
        product_divs = all_divs.find('div', {'class' : 'product-wrap'})
        if product_divs is not None: 
            href_url = product_divs.find('a')
            driver.quit() # closing the webdriver
            return href_url['href']
        else:
            driver.quit() # closing the webdriver
            return None   
         
        

    def get_fromWithenew(self, page_url):
        # page_url = "https://wethenew.com" + url
        response = requests.get(page_url)
        # Now, we could simply apply bs4 to html variable 
        soup = BeautifulSoup(response.content, "html.parser") 
        all_divs = soup.find('div', {'class' : 'select'})
        price_size = []
        if all_divs is not None: 
            select = all_divs.find('select')
            option_list = select.contents
            for each in option_list:
                if each == ' ':
                    continue
                str = each.text.split('-')
                if str[2] == ' Indisponible':
                    str[2] = '-'
                size = size  = re.findall(r'[-+]?\d*\.\d+|\d+', str[1])
                if '€' in str[2]:
                    # res = re.findall(r'\d+', str[2])
                    # usd_value = c.convert(int(res[0]), 'EUR', 'USD')
                    price = str[2].replace('€', '').strip()
                    price_size.append([size[0], price])
            return price_size
        else:
            return None

# class scraperThread_forWithenew(threading.Thread):
#      def __init__(self, _styleId):
#         threading.Thread.__init__(self)
#         self._styleId = _styleId
#      def run(self):
#         # Get lock to synchronize threads
#         threadLock.acquire()
#         thread_for_withenew(self._styleId)
#         # Free lock to release next thread
#         threadLock.release()


def thread_for_withenew(styleId):
    url = withenew_1.search_ByStyleId(styleId)
    if url is not None:
        page_url = "https://wethenew.com" + url
        size_priceInfo = withenew_1.get_fromWithenew(page_url)
        if(size_priceInfo is not None):
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_wethenew_priceSize":size_priceInfo}})
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_wethenew_url":page_url}})
            print("success of scraping from Withenew")
        else:
            print("product not exist in Withenew")
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_wethenew_priceSize":"-"}})
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_wethenew_url":"-"}})
                
    else:
        print("product not exist in Withenew")
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_wethenew_priceSize":"-"}})
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_wethenew_url":"-"}})

def thread_for_withenewByURL(page_url, styleId):
    size_priceInfo = withenew_1.get_fromWithenew(page_url)
    if(size_priceInfo is not None):
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_wethenew_priceSize":size_priceInfo}})
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_wethenew_url":page_url}})
        print("success of scraping from Withenew")
    else:
        print("product not exist in Withenew")
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_wethenew_priceSize":"-"}})
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_wethenew_url":"-"}})



def update_function(sku_id):
    thread_wethenew = scraperThread_forWithenew(sku_id)
    thread_wethenew.start()
    thread_wethenew.join()
    # thread_for_withenew(sku_id)
    return "Finished wethenew..."


if __name__ == "__main__":

    withenew_1 = Withenew()
    # threadLock = threading.Lock()
    try: 
        conn = MongoClient() 
        print("Connected successfully!!!") 
    except:   
        print("Could not connect to MongoDB") 
    db = conn.sneaks4sure 
    # Created or Switched to collection names
    collection = db.Sneakers
    print("updating.....")
    sku_id = sys.argv[1]
    # sku_id = "150204C"
    cursor_list = collection.find({'product_sku_id': {'$regex':sku_id}})
    for product in cursor_list:
        if "product_wethenew_url"  in product and "https://wethenew.com" in product['product_wethenew_url']:
            product_url =  product['product_wethenew_url']
            thread_for_withenewByURL(product_url, sku_id)
        elif "product_wethenew_url"  in product and "-" in product['product_wethenew_url']:
            continue
        else:
            update_function(sku_id)
