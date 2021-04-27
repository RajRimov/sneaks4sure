
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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW
import re
from currency_converter import CurrencyConverter
from proxy import get_random_hdr, get_random_proxy


class Kikikickz:
    def __init__(self, url = None, stylId = None):
        self.url = ''
        self.stylId = ''

    def search_ByStyleId(self, stylId):
        url = 'https://kikikickz.com/search?type=product&q={}'.format(stylId)
        # url = 'https://kikikickz.com/search?type=product&q={}'.format("554724-077")
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
        all_divs = soup.find('div', {'class' : 'grid-product__content'})
        if all_divs is not None: 
            href_url = all_divs.find('a')
            driver.quit() # closing the webdriver 
            return "https://kikikickz.com" + href_url['href']
        else:
            driver.quit() # closing the webdriver 
            return None   
        
        

    def get_fromKikikickz(self, url):
        page_url = url
        response = requests.get(page_url)
        # Now, we could simply apply bs4 to html variable 
        soup = BeautifulSoup(response.content, "html.parser") 
        script_content = soup.find('div', {'class' : 'variant-input-wrap'})
        price_size = []
        try:
            if script_content is not None: 
                select = script_content.find('select')
                option_list = select.contents
                for each in option_list:
                    if each == ' ' or each  == '\n':
                        continue
                    str = each.text.split('-')
                    if str[2] == ' Indisponible':
                        str[2] = '-'
                    if 'US' in str[1]:
                        size = re.findall(r'[-+]?\d*\.\d+|\d+', str[1])
                    if '€' in str[2]:
                        price = str[2].replace('€ ', '').strip()
                        # usd_value = c.convert(int(res[0]), 'EUR', 'USD')
                        price_size.append([size[0], price])
                return price_size
            else:
                return None
        except Exception as ex:
            return None

class scraperThread_forKikikickz(threading.Thread):
     def __init__(self, _styleId):
         threading.Thread.__init__(self)
         self._styleId = _styleId
     def run(self):
         # Get lock to synchronize threads
         threadLock.acquire()
         thread_for_Kikikickz(self._styleId)
         # Free lock to release next thread
         threadLock.release()


def thread_for_Kikikickz(styleId):
    url = kikikickz_instance.search_ByStyleId(styleId)
    if url is not None:
        product_url = url
        # print("success of adding the url from Kikikickz")
        size_priceInfo = kikikickz_instance.get_fromKikikickz(url)
        if size_priceInfo is not None:
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Kikikickz_priceSize":size_priceInfo}})
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Kikikickz_url":product_url}})
            print("success of adding the price-size info from KickScrew")
            
        else:
            print("product not exist in Kikikickz")
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Kikikickz_priceSize":"-"}})
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Kikikickz_url":"-"}})
    else:
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Kikikickz_url":"-"}})
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Kikikickz_priceSize":"-"}})
        print("product not exist in Kikikickz")


def thread_for_KikikickzByURL(product_url, styleId):
    size_priceInfo = kikikickz_instance.get_fromKikikickz(product_url)
    if size_priceInfo is not None:
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Kikikickz_priceSize":size_priceInfo}})
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Kikikickz_url":product_url}})
        print("success of adding the price-size info from KickScrew")
        
    else:
        print("product not exist in Kikikickz")
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Kikikickz_priceSize":"-"}})
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Kikikickz_url":"-"}})

def update_function(sku_id):
    thread_Kikikickz = scraperThread_forKikikickz(sku_id)
    thread_Kikikickz.start()
    thread_Kikikickz.join()
    # thread_for_Kikikickz(sku_id)
    return "Finished kikikickz...."

if __name__ == "__main__":

    kikikickz_instance = Kikikickz()
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
    cursor_list = collection.find({'product_sku_id': {'$regex':sku_id}})
    for product in cursor_list:
        if "product_Kikikickz_url"  in product and "https://kikikickz.com/" in product['product_Kikikickz_url']:
            product_url =  product['product_Kikikickz_url']
            thread_for_KikikickzByURL(product_url, sku_id)
        elif "product_Kikikickz_url"  in product and "-" in product['product_Kikikickz_url']:
            continue
        else:
            update_function(sku_id)
    print("finished.....")
