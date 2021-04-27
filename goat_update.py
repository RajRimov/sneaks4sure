import sys
sys.path.append("C:\Sneaks4Sure\Scrapper\my_env\Lib\site-packages")
from datetime import date
from pymongo import MongoClient
import requests
import threading
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from currency_converter import CurrencyConverter
from selenium import webdriver 
import time
import re
import json
from proxy import get_random_hdr, get_random_proxy, get_random_proxy_forGoat

proxy = {
        'http':'http://oliversulej3:guT0XPvk@194.135.18.42:32624',
        'https': 'https://oliversulej3:guT0XPvk@194.135.18.42:32624'                   
    }


base_header = { 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,ko;q=0.8',
        'cache-control': 'max-age=0',
        'cookie': '__cfduid=d4c4c72c8d37b362c29c87137dcb793a41612681379',
        'if-none-match': 'W/"316e8-pHkcGW3MowNDVO90tVesLxegkYs"',
        'sec-fetch-dest': 'document' ,
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}


#check if the new styleId already exists in database
def alreadyExists(new_skuId):
     if collection.find({'product_sku_id': new_skuId}).count() > 0:
         return True
     else:
         return False

class Goat:
    def __init__(self, url = None, stylId = None):
        self.url = ''
        self.stylId = ''

    def search_ByStyleId(self, stylId):
        url = 'https://www.goat.com/search?query={}'.format(stylId)
        # url = 'https://www.goat.com/sneakers/wmns-air-jordan-1-high-og-unc-to-chicago-cd0461-046'
        chrome_options = webdriver.ChromeOptions()
        proxy= get_random_proxy_forGoat()
        # proxy = "200.0.61.74:6149"
        # proxy = "200.0.61.48:6123"
        i = 0
        chrome_options.add_argument('--proxy-server=%s' % proxy)
        while True:
            try:
                i = i + 1
                
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(url)
                time.sleep(5) 
                if i > 10:
                    break
                html = driver.page_source 
                # Now, we could simply apply bs4 to html variable 
                soup = BeautifulSoup(html, "html.parser") 
                if "Attention Required!" in soup.text or "This page isn’t working" in soup.text or soup.text == '':
                    proxy = get_random_proxy_forGoat()
                    chrome_options.add_argument('--proxy-server=%s' % proxy)
                    driver.quit()
                    continue
                break
            except:
                try:
                    driver.quit()
                    proxy = get_random_proxy_forGoat()
                    chrome_options.add_argument('--proxy-server=%s' % proxy)
                except:
                    break
                    
        # time.sleep(5)ProductTitlePaneActions__ButtonTextWrapper-l1sjea-2 eqjXpc
        # all_divs = soup.find('div', {'class' : 'ProductTitlePaneActions__ButtonTextWrapper-l1sjea-2 eqjXpc'})
        all_divs = soup.find('div', {'class' : 'Grid__CellContent-sc-1njij7e-1 iZedTG'})
        if all_divs is not None: 
            href_url = all_divs.find('a')
            driver.quit() # closing the webdriver
            return href_url['href'], chrome_options
        else:
            driver.quit() # closing the webdriver
            return None, chrome_options   
        # driver.quit() # closing the webdriver 
        

    def get_fromGoat(self, url):
        proxy = get_random_proxy()
        hdr = get_random_hdr()
        hhdr = hdr.strip();
        base_header["if-none-match"] = hhdr
        page_url = "https://www.goat.com/web-api/v1/product_variants?productTemplateId=" + url
        # res
        # reponse = requests.get(page_url, headers=base_header, proxies = proxy, verify = False)
        i = 0
        proxy = {
        'http':'http://oliversulej3:guT0XPvk@194.135.18.42:32624',
        'https': 'https://oliversulej3:guT0XPvk@194.135.18.42:32624'                   
        }
        resp = ''
        while True:
            try:
                resp = requests.get(page_url, headers=base_header, proxies = proxy, verify = False)
                if resp.status_code == 403 or resp.status_code == 502:
                    proxy = get_random_proxy()
                    hdr = get_random_hdr()
                    hhdr = hdr.strip();
                    base_header["if-none-match"] = hhdr
                    continue
                break
            except Exception as ex:
                proxy = get_random_proxy()
                hdr = get_random_hdr()
                hhdr = hdr.strip();
                base_header["if-none-match"] = hhdr
                i = i + 1
                if i >= 8:
                    break
                print("connection error...{}--->".format(i), ex)
        # Now, we could simply apply bs4 to html variable 
        if resp != '':
            if resp.status_code ==  200:
                soup = BeautifulSoup(resp.content, "html.parser")
                size_length = len(json.loads(soup.text))
                size_json = json.loads(soup.text)
                size_price =  []
                for index in range(size_length):
                    if size_json[index]['boxCondition'] == 'good_condition':
                        s = size_json[index]['size']
                        p = size_json[index]['lowestPriceCents']['amount']/100
                        size_price.append([s, int(p)])
                return size_price
            else:
                return None
        else:
            return None

class scraperThread_forGoat(threading.Thread):
     def __init__(self, _styleId):
         threading.Thread.__init__(self)
         self._styleId = _styleId
     def run(self):
         # Get lock to synchronize threads
         threadLock.acquire()
         thread_for_goat(self._styleId)
         threadLock.release()


def thread_for_goat(styleId):
    url, chrome_options = goat_1.search_ByStyleId(styleId)
    if url is not None: 
        product_url = "https://www.goat.com" +  url
        real_url  = url.split("/")

        size_priceInfo = goat_1.get_fromGoat(real_url[2])
        if size_priceInfo is not None:
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_goat_priceSize":size_priceInfo}})
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_goat_url":product_url}})
            print("success of scraping from goat")
        else:
            print("product not exist in goat")
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_goat_priceSize":"-"}})
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_goat_url":"-"}})
    else:
        print("product not exist in goat")
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_goat_priceSize":"-"}})
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_goat_url":"-"}})



def update_function(sku_id):
    # thread_goat = scraperThread_forGoat(sku_id)
    # thread_goat.start()
    # thread_goat.join()
    goat_1.get_ByURL('')
    return "goat finished...."   
    
if __name__ == "__main__":
    
    goat_1 = Goat()
    threadLock = threading.Lock()
    try: 
        conn = MongoClient() 
        print("Connected successfully!!!") 
    except:   
        print("Could not connect to MongoDB") 
    # database 
    db = conn.sneaks4sure 
    # Created or Switched to collection names
    collection = db.Sneakers
    # sku_id = sys.argv[1]
    # brand = "asics"
    sku_id = "166800C"
    update_function(sku_id)
    
