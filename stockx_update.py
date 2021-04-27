
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
import csv





#check if the new styleId already exists in database
def alreadyExists(new_skuId):
    if collection.find({'product_sku_id': new_skuId}).count() > 0:
        return True
    else:
        return False

def get_price_withProxy(url, proxy):
    chrome_options = webdriver.ChromeOptions()
    # proxy= get_random_proxy_forGoat()
    # proxy = "200.0.61.74:6149"
    # proxy = "200.0.61.48:6123"
    i = 0
    chrome_options.add_argument('--proxy-server=%s' % proxy)
    sign_proxy_list = []
    us_proxy_list = []
    # proxy_success = proxy
    while True:
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            time.sleep(5) 
            html = driver.page_source 
            # Now, we could simply apply bs4 to html variable 
            soup = BeautifulSoup(html, "html.parser") 
            if "Attention Required!" in soup.text or "This page isn’t working" in soup.text or soup.text == '':
                sign_proxy_list.append(proxy)
                with open('Sign-Proxy.txt', 'a+') as f:
                    f.write('%s\n' % proxy)
                proxy = get_random_proxy_forGoat()
                chrome_options.add_argument('--proxy-server=%s' % proxy)
                driver.quit()
                continue
            break
        except:
            # try:
            #     driver.quit()
            #     proxy_success = get_random_proxy_forGoat()
            #     chrome_options.add_argument('--proxy-server=%s' % proxy_success)
            # except:
            # driver.quit()
            proxy = get_random_proxy_forGoat()
            chrome_options.add_argument('--proxy-server=%s' % proxy)
            pass
    all_divs = soup.find('div', {'class' : 'select-options'})
    price_size = []
    last_sale_price = ''
    if all_divs is not None: 
        ul_div = all_divs.find('ul')
        li_list = ul_div.contents
        for div_tag in li_list:
            size_info = div_tag.find('div', {'class':'title'}).text
            price_info = div_tag.find('div', {'class':'subtitle'}).text
            if size_info == "us All" or price_info == "Bid":
                continue
            size = re.findall(r'[-+]?\d*\.\d+|\d+', size_info)
            if '$' in price_info:
                usd_value = price_info.replace('$', "").replace(",", "")
                with open('US-Proxy.txt', 'a+') as f:
                    f.write('%s\n' % proxy)
                # euro_value = c.convert(int(res),'USD', 'EUR')
            if '€' in price_info:
                euro_value = float(price_info.replace('€', "").replace(",", ""))
                price_size.append([size[0].strip(), round(euro_value)])
        last_sale_div = soup.find('div', {'class' : 'sale-value'}).text
        if '€' in last_sale_div:
            last_sale_price = last_sale_div.replace('€', "").replace(",", "")
        driver.quit() # closing the webdriver 
        return price_size, proxy, last_sale_price
    else:
        driver.quit() # closing the webdriver 
        return None, proxy, last_sale_price
def get_price_size(url):
    proxy, chrome_options = get_random_proxy()
    i = 0
    while True:
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            time.sleep(5) 
            html = driver.page_source 
            # Now, we could simply apply bs4 to html variable 
            soup = BeautifulSoup(html, "html.parser") 
            if "This site can’t be reached" in soup.text or "This page isn’t working" in soup.text or "No internet" in soup.text:
                proxy, chrome_options = get_random_proxy()
                driver.quit()
                continue
            break
        except:
            try:
                # i = i + 1
                # if i > 8:
                #     break
                driver.quit()
                proxy, chrome_options = get_random_proxy()
            except:
                pass
    # soup = BeautifulSoup(response.content, "lxml") 
    # print(soup.prettify())
    all_divs = soup.find('div', {'class' : 'select-options'})
    price_size = []
    if all_divs is not None: 
        ul_div = all_divs.find('ul')
        li_list = ul_div.contents
        for div_tag in li_list:
            size_info = div_tag.find('div', {'class':'title'}).text
            price_info = div_tag.find('div', {'class':'subtitle'}).text
            if size_info == "us All" or price_info == "Bid":
                continue
            size = re.findall(r'[-+]?\d*\.\d+|\d+', size_info)
            if '$' in price_info:
                usd_value = int(price_info.replace('$', "").replace(",", ""))
                # euro_value = c.convert(int(res),'USD', 'EUR')
            if '€' in price_info:
                euro_value = float(price_info.replace('€', "").replace(",", ""))
                price_size.append([size[0].strip(), round(euro_value)])
        last_sale_div = soup.find('div', {'class' : 'sale-value'}).text
        if '€' in last_sale_div:
            last_sale_price = float(last_sale_div.replace('€', "").replace(",", ""))
        driver.quit() # closing the webdriver 
        return price_size, last_sale_price
    else:
        driver.quit() # closing the webdriver 
        return None   
class scraperThread_forStockx(threading.Thread):
     def __init__(self, urlkey, skuId, init_proxy):
        threading.Thread.__init__(self)
        self.urlkek = urlkey
        self.skuId = skuId
        self.init_proxy = init_proxy
     def run(self):
        # Get lock to synchronize threads
        threadLock.acquire()
        thread_for_update(self.urlkek, self.skuId,self.init_proxy)
        # Free lock to release next thread
        threadLock.release()

def thread_for_update(urlKey, skuId, init_proxy):    

    price_info, return_proxy, last_sale_price = get_price_withProxy(urlKey, init_proxy)
    init_proxy = return_proxy
    if alreadyExists(skuId) and price_info is not None:
        collection.update_one({'product_sku_id': skuId}, {'$set':{"product_priceSize":price_info}})
        collection.update_one({'product_sku_id': skuId}, {'$set':{"product_last_sale":last_sale_price}})
        print("success of updating price-size.....")
    else:
        print("price-size is None....")
    


def stockx_update(sku_id, init_proxy):
    cursor_list = collection.find({'product_sku_id': {'$regex':sku_id}})
    for doc in cursor_list:
        stockx_thread = scraperThread_forStockx(doc['product_stock_url'], doc['product_sku_id'], init_proxy)
        stockx_thread.start()
        stockx_thread.join()
        # thread_for_update(doc['product_stock_url'], doc['product_sku_id'])
    return "stockx finished....."
    # thread_for_update(urlkey_list, skuId_list)

if __name__ == "__main__":

    # flag for updating the scraped data.
    try: 
        conn = MongoClient() 
        print("Connected successfully!!!") 
    except:   
        print("Could not connect to MongoDB") 
    # database 
    db = conn.sneaks4sure 
    
    # Created or Switched to collection names: my_gfg_collection 
    collection = db.Sneakers

    c = CurrencyConverter()
    #stockx = StockXAPI()
    threadLock = threading.Lock()
    init_proxy =  get_random_proxy_forGoat()
    # init_proxy = "194.33.61.96:8679"
    sku_id = sys.argv[1]

    # sku_id = "166800C"
    stockx_update(sku_id, init_proxy)

