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
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sneaks_model import Sneak
from proxy import get_random_hdr, get_random_proxy


#check if the new styleId already exists in database
def alreadyExists(new_skuId):
     if collection.find({'product_sku_id': new_skuId}).count() > 0:
         return True
     else:
         return False


class FlightClub:
     def __init__(self, url = None, stylId = None):
          self.url = ''
          self.stylId = ''

     def search_ByStyleId(self, stylId):
          # url = 'https://www.flightclub.com/catalogsearch/result?query={}'.format("440888 140")
          url = 'https://www.flightclub.com/catalogsearch/result?query={}'.format(stylId)
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
          # # Now, we could simply apply bs4 to html variable 
          # soup = BeautifulSoup(html, "html.parser")
          all_divs = soup.find('div', {'class' : 'sc-10ono97-0 eHjXsh'})
          if all_divs is not None: 
               href_url = all_divs.find('a')
               driver.quit() # closing the webdriver 
               return href_url['href']
          else:
               driver.quit() # closing the webdriver 
               return None   
        
        

     def get_fromFlight(self, url):
          # page_url = "https://www.flightclub.com" + url
          response = requests.get(url)
          # Now, we could simply apply bs4 to html variable 
          soup = BeautifulSoup(response.content, "html.parser")
          size_divs = soup.find('div', {'class' : 'sc-1oe5l4r-4 cfOdiJ'})
          size_list = []
          if size_divs is not None: 
               buttons = size_divs.find_all('button')
               for button in buttons:
                    size_list.append(button.text)
          else:
               return None
          all_scripts = soup.find_all('script', {'type' : 'application/ld+json'})

          price_info_script = json.loads(all_scripts[1].string)
          size_price =  []
          if price_info_script is not None and "offers" in price_info_script:
               json_object = price_info_script["offers"]["offers"]
               for index in range(len(json_object)):
                    size = size_list[index]
                    price = json_object[index]["price"]
                    size_price.append([size, price])
               return size_price
          else: 
               return None

class scraperThread_forFlight(threading.Thread):
     def __init__(self, _styleId):
         threading.Thread.__init__(self)
         self._styleId = _styleId
     def run(self):
         # Get lock to synchronize threads
         threadLock.acquire()
         thread_for_flight(self._styleId)
         # Free lock to release next thread
         threadLock.release()


def thread_for_flight(styleId):
     url = flight.search_ByStyleId(styleId)
     if url is not None:
          page_url = "https://www.flightclub.com" + url
          size_priceInfo = flight.get_fromFlight(page_url)
          if(size_priceInfo is not None):
               collection.update_one({'product_sku_id': styleId}, {'$set':{"product_flight_priceSize":size_priceInfo}})
               collection.update_one({'product_sku_id': styleId}, {'$set':{"product_flight_url":page_url}})
               print("success of scraping from Flight Club")
               
          else:
               print("product not exist in Flight Club")
               collection.update_one({'product_sku_id': styleId}, {'$set':{"product_flight_url":"-"}})
               collection.update_one({'product_sku_id': styleId}, {'$set':{"product_flight_priceSize":"-"}})
     else:
          print("product not exist in Flight Club")
          collection.update_one({'product_sku_id': styleId}, {'$set':{"product_flight_url":"-"}})
          collection.update_one({'product_sku_id': styleId}, {'$set':{"product_flight_priceSize":"-"}})

def thread_for_flightbyURL(page_url, styleId):
     size_priceInfo = flight.get_fromFlight(page_url)
     if(size_priceInfo is not None):
          collection.update_one({'product_sku_id': styleId}, {'$set':{"product_flight_priceSize":size_priceInfo}})
          collection.update_one({'product_sku_id': styleId}, {'$set':{"product_flight_url":page_url}})
          print("success of scraping from Flight Club")
          
     else:
          print("product not exist in Flight Club")
          collection.update_one({'product_sku_id': styleId}, {'$set':{"product_flight_url":"-"}})
          collection.update_one({'product_sku_id': styleId}, {'$set':{"product_flight_priceSize":"-"}})


def update_function(sku_id):
     thread_flight = scraperThread_forFlight(sku_id)
     thread_flight.start()
     thread_flight.join()
     # thread_for_flight(sku_id)
     return "FlightClub finished..."

if __name__ == "__main__":
    
     
     # flag for updating the scraped data.
     # update_flag = True
     flight = FlightClub()
     threadLock = threading.Lock()
     try: 
          conn = MongoClient() 
          print("Connected successfully!!!") 
     except:   
          print("Could not connect to MongoDB") 
     # database 
     db = conn.sneaks4sure 
     # Created or Switched to collection names: my_gfg_collection 
     collection = db.Sneakers
     sku_id = sys.argv[1]
     # sku_id = "166800C"
     cursor_list = collection.find({'product_sku_id': {'$regex':sku_id}})
     for product in cursor_list:
          if "product_flight_url"  in product and "https://www.flightclub.com/" in product['product_flight_url']:
               product_url =  product['product_flight_url']
               thread_for_flightbyURL(product_url, sku_id)
          elif "product_flight_url"  in product and "-" in product['product_flight_url']:
                continue
          else:
               update_function(sku_id)
