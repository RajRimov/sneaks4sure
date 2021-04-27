
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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from proxy import get_random_hdr, get_random_proxy


class kickScrew:
    def __init__(self, url = None, stylId = None):
        self.url = ''
        self.stylId = ''

    def search_ByStyleId(self, stylId):
          # url = 'https://www.kickscrew.com/?q={}'.format("510815-101")
          url = 'https://www.kickscrew.com/?q={}'.format(stylId)
          # proxy, chrome_options = get_random_proxy()
          # driver = webdriver.Chrome(options=chrome_options)
          # while True:
          #      try:
          #           driver = webdriver.Chrome(options=chrome_options)
          #           driver.get(url)
          #           time.sleep(5) 
          #           html = driver.page_source 
          #           # Now, we could simply apply bs4 to html variable 
          #           soup = BeautifulSoup(html, "html.parser") 
          #           if "This site can’t be reached" in soup.text:
          #                proxy, chrome_options = get_random_proxy()
          #                drive.close()
          #                continue
          #           break
          #      except:
          #           proxy, chrome_options = get_random_proxy()
          #           # driver.quit() 
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
          all_divs = soup.find('div', {'class' : 'result-wrapper'})
          if all_divs is not None: 
               href_url = all_divs.find('a')
               driver.quit() # closing the webdriver 
               return href_url['href']
          else:
               driver.quit() # closing the webdriver 
               return None   
          # driver.quit() # closing the webdriver 
        

    def get_fromKickScrew(self, url):
          page_url = url
          try:
               response = requests.get(page_url)
          except:
               return None
          # Now, we could simply apply bs4 to html variable 
          soup = BeautifulSoup(response.content, "html.parser") 
          script_content = soup.find('script', {'type' : 'application/ld+json'})
          if script_content is not None:
               size_priceInfo = json.loads(script_content.string)
          else:
               return None
          if "offers" in size_priceInfo:
               if "offers" in size_priceInfo['offers']:
                    sku_info = size_priceInfo['sku'] + '-'
                    json_object = size_priceInfo["offers"]["offers"]
                    size_length = len(size_priceInfo["offers"]["offers"])
                    size_price =  []
                    for index in range(size_length):
                         p = json_object[index]['price']
                         s = json_object[index]['sku']
                         size = s.replace(sku_info, '')
                         res = re.findall(r'\d+', size)
                         if len(res) != 0:
                              size_val = int(res[0])/10
                              size_price.append([size_val, p])
                    return size_price
               else: 
                    return None
          else: 
               return None

class scraperThread_forKickScrew(threading.Thread):
     def __init__(self, _styleId):
         threading.Thread.__init__(self)
         self._styleId = _styleId
     def run(self):
         # Get lock to synchronize threads
         threadLock.acquire()
         thread_for_kickscrew(self._styleId)
         threadLock.release()


def thread_for_kickscrew(styleId):
     url = kickscrew.search_ByStyleId(styleId)
     if url is not None:
          product_url = url
          size_priceInfo = kickscrew.get_fromKickScrew(url)
          if size_priceInfo is not None:
               collection.update_one({'product_sku_id': styleId}, {'$set':{"product_KickScrew_url":product_url}})
               collection.update_one({'product_sku_id': styleId}, {'$set':{"product_KickScrew_priceSize":size_priceInfo}})
               print("success of scraping from KickScrew")
               
          else:
               print("product not exist in KickScrew")
               collection.update_one({'product_sku_id': styleId}, {'$set':{"product_KickScrew_url":product_url}})
               collection.update_one({'product_sku_id': styleId}, {'$set':{"product_KickScrew_priceSize":"-"}})
     else:
          collection.update_one({'product_sku_id': styleId}, {'$set':{"product_KickScrew_url":"-"}})
          collection.update_one({'product_sku_id': styleId}, {'$set':{"product_KickScrew_priceSize":"-"}})
          print("product not exist in KickScrew")

def thread_for_kickscrewByURL(product_url, styleId):
     size_priceInfo = kickscrew.get_fromKickScrew(product_url)
     if size_priceInfo is not None:
          collection.update_one({'product_sku_id': styleId}, {'$set':{"product_KickScrew_url":product_url}})
          collection.update_one({'product_sku_id': styleId}, {'$set':{"product_KickScrew_priceSize":size_priceInfo}})
          print("success of scraping from KickScrew")
          
     else:
          print("product not exist in KickScrew")
          collection.update_one({'product_sku_id': styleId}, {'$set':{"product_KickScrew_url":"-"}})
          collection.update_one({'product_sku_id': styleId}, {'$set':{"product_KickScrew_priceSize":"-"}})

def update_function(sku_id):
     thread_KickScrew = scraperThread_forKickScrew(sku_id)
     thread_KickScrew.start()
     thread_KickScrew.join()
     # thread_for_kickscrew(sku_id)
     return "KicksCrew finisehd..."

if __name__ == "__main__":

     kickscrew = kickScrew()
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
     # sku_id = "CD0461-046"
     cursor_list = collection.find({'product_sku_id': {'$regex':sku_id}})
     for product in cursor_list:
          if "product_KickScrew_url"  in product and "https://www.kickscrew.com/" in product['product_KickScrew_url']:
               product_url =  product['product_KickScrew_url']
               thread_for_kickscrewByURL(product_url, sku_id)
          elif "product_KickScrew_url"  in product and "-" in product['product_KickScrew_url']:
                continue
          else:
               update_function(sku_id)
     print("finished.....")
