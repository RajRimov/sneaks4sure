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
from python_graphql_client import GraphqlClient
from currency_converter import CurrencyConverter

class Klekt:
    def __init__(self, url = None, stylId = None):
        self.url = ''
        self.stylId = ''

    def search_ByStyleId(self, stylId):
        # Create the query string and variables required for the request.
        query = """
            query SearchProducts($input: SearchInput!) {
                search(input: $input) {
                    items {
                    productId
                    currencyCode
                    slug
                    }
                }
            }"""
        variables = {
                    "input": {
                        "term": stylId,
                        # "term": "H6C3K-6969",
                        "sizeType": None,
                        "facetValueIds": [],
                        "groupByProduct": True,
                        "facetSlugs": [],
                        "availability": "available",
                        "take": 6,
                        "skip": 0,
                        "sort": {
                        "featured": "DESC"
                        }
                    }
                    }

        # Synchronous request
        data = client.execute(query=query, variables=variables, verify=False)
        items = data["data"]["search"]["items"]
        if len(items) != 0:
            for item in items:
                if "slug" in item:
                    product_slug = data["data"]["search"]["items"][0]["slug"]
                    # product_url = "https://www.klekt.com/product/" + product_slug
        else:
            product_slug = None
            # product_url = None
        return product_slug
        

    def get_fromKlekt(self, product_slug):
        product_url = "https://www.klekt.com/product/" + product_slug
        variables = {'slug': product_slug}
        # Create the query string and variables required for the request.
        query = """
            query productDetail($slug: String){
                productDetails(slug: $slug){
                    name
                    id
                    variants{
                    id
                    name
                    price
                    priceWithTax
                    currencyCode
                    }
                }
            }"""
        # Synchronous request
        data = client.execute(query=query, variables=variables, verify=False)
        size_price = []
        product_variants = data["data"]["productDetails"]["variants"]
        for each in product_variants:
            size_info = each["name"]
            price_info = each["priceWithTax"]
            currency = each["currencyCode"]
            
            size = re.findall(r'[-+]?\d*\.\d+|\d+', size_info)
            if len(size) == 0:
                continue
            else:
                for i in range(0, len(size)):
                    if size[i] == '':
                        continue
            # price_tax = re.findall(r'[-+]?\d*\.\d+|\d+', price_info)
            if currency == "EUR":
                price = int(price_info)/100
                # usd_value = c.convert(price, 'EUR', 'USD')
                size_price.append([size[0], int(price)])
        return size_price
          

class scraperThread_forKlekt(threading.Thread):
     def __init__(self, _styleId):
         threading.Thread.__init__(self)
         self._styleId = _styleId
     def run(self):
         # Get lock to synchronize threads
         threadLock.acquire()
         thread_for_Klekt(self._styleId)
         # Free lock to release next thread
         threadLock.release()


def thread_for_Klekt(styleId):
    slug = Klekt_instance.search_ByStyleId(styleId)
    if slug is not None:
        url = "https://www.klekt.com/product/" + slug
        size_priceInfo = Klekt_instance.get_fromKlekt(slug)
        if size_priceInfo is not None:
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Klekt_priceSize":size_priceInfo}})
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Klekt_url":url}})
            # print("success of scraping from Klekt")
            
        else:
            # print("product not exist in Klekt")
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Klekt_priceSize":"-"}})
            collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Klekt_url":"-"}})
    else:
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Klekt_url":"-"}})
        collection.update_one({'product_sku_id': styleId}, {'$set':{"product_Klekt_priceSize":"-"}})
        # print("product not exist in Klekt")


def update_function(sku_id):
    thread_Klekt = scraperThread_forKlekt(sku_id)
    thread_Klekt.start()
    thread_Klekt.join()
    # thread_for_Klekt(sku_id)
    return print("Finished...")

if __name__ == "__main__":

    Klekt_instance = Klekt()
    c = CurrencyConverter()
    # Instantiate the client with an endpoint.
    client = GraphqlClient(endpoint="https://apiv2.klekt.com/shop-api?vendure-token=iqrhumfu2u9mumwq369")
    threadLock = threading.Lock()
    try: 
        conn = MongoClient() 
        # print("Connected successfully!!!") 
    except:   
        print("Could not connect to MongoDB") 
    sneaker_1 = Sneak()
    # database 
    db = conn.sneaks4sure 
    collection = db.Sneakers
    # print("updating....")
    sku_id = sys.argv[1]
    update_function(sku_id)
    # print("finished.....")
