import json
from datetime import datetime
import requests
import base64
from bs4 import BeautifulSoup
import numpy as np
from proxy import get_random_hdr, get_random_proxy
import ssl

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
        'Host': 'stockx.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}


class StockXAPI:
    def __init__(self, username=None, password=None):
        self.username = ''
        self.password = ''
        self.client_id = ''
        self.token = ''
        
        if username and password:
            self.login(username, password)

    def _process_json(self, json_data, output_data):
        # Split output data categories into first and second layers
        return_data = [i for i in output_data if type(i) == str]
        secondary_return_data = [i for i in output_data if type(i) == list]

        product_data = {}

        # Add categories from output_data that are in the json to product_data
        for key in return_data:
            if key in json_data:
                product_data[key] = json_data[key]

        for top_key, bottom_key in secondary_return_data:
            for key in json_data[top_key]:
                if key == bottom_key:
                    product_data[bottom_key] = json_data[top_key][bottom_key]

        return product_data

 
    def search_items(self, search_term, output_data,  proxy, page, max_searches=50):
        
        search_term = search_term.replace(' ', '%20')
        url = 'https://stockx.com/api/browse?&page={}&_search={}&dataType=product&country=US'.format(page, search_term)
        print("page={}, search_term = {}".format( page, search_term))
        # Get the product list and add each product to final_data.
        i = 0
        final_data = []
        while True:
            try:
                #print(i)
                print("search-try", i)
                resp = requests.get(url, headers=base_header, proxies = proxy, verify = False)
                data = json.loads(resp.content)['Products'][:max_searches]
                for item in data:
                    final_data.append(self._process_json(item, output_data))
                break
            except Exception as ex:
                i = i + 1
                hdr = get_random_hdr()
                hhdr = hdr.strip();
                base_header["if-none-match"] = hhdr
                proxy = get_random_proxy()
                
                print("connection error...{}--->".format(i), ex)
            
        return final_data, proxy


    def get_item_data(self, item_id,  proxy, output_data):
        url = 'https://stockx.com/api/products/{}'.format(item_id)
        
        i = 0
        while True:
            try:
                print("item - try", url)
                resp = requests.get(url, headers=base_header, proxies = proxy, verify = False)
                break
            except Exception as ex:
                i = i + 1
                hdr = get_random_hdr()
                hhdr = hdr.strip();
                base_header["if-none-match"] = hhdr
                proxy = get_random_proxy()
                print("connection error...{}--->".format(i), ex)
        while resp.status_code != 200:
            try:
                print("item - response", url)
                resp = requests.get(url, headers=base_header, proxies = proxy, verify = False)
                break
            except Exception as ex:
                i = i + 1
                hdr = get_random_hdr()
                hhdr = hdr.strip();
                base_header["if-none-match"] = hhdr
                proxy = get_random_proxy()
                print("connection error...{}--->".format(i), ex)
        try:
            data = json.loads(resp.content)['Product']
        except:
            return None, proxy
        # Get the market data for the item.
        market_data_url = 'https://stockx.com/api/products/{}/market'.format(item_id)        
        i = 0
        final_data = []
        while True:
            try:
                print("market - try", i)
                resp = requests.get(market_data_url, headers=base_header, proxies = proxy, verify = False)
                break
            except Exception as ex:
                hdr = get_random_hdr()
                hhdr = hdr.strip();
                base_header["if-none-match"] = hhdr
                proxy = get_random_proxy()
                i = i + 1
                print("connection error...{}--->".format(i), ex)
        i = 0
        while resp.status_code != 200:
            try:
                print("market - response", i)
                resp = requests.get(market_data_url, headers=base_header, proxies = proxy, verify = False)
                break
            except Exception as ex:
                hdr = get_random_hdr()
                hhdr = hdr.strip();
                base_header["if-none-match"] = hhdr
                proxy = get_random_proxy()
                i = i + 1
                print("response statuscode  error...{}--->".format(i), ex)
        try:
            market_data = json.loads(resp.content)['Market']
            data['market'] = market_data
            final_data = self._process_json(data, output_data)
            return final_data, proxy
        except:
            return None, proxy

    def get_price_size(self, url_key, proxy, output_data):
        url = 'https://stockx.com/api/products/{}?includes=market'.format(url_key)
        final_data = []
        i = 0
        while True:
            try:
                print("price - try", i)
                resp = requests.get(url, headers=base_header, proxies = proxy, verify = False)
                data = json.loads(resp.content)['Product']['children']
                
                for each in data:
                    shoe_size = data[each]['shoeSize']
                    shoe_price = data[each]['market']['lowestAsk']
                    final_data.append([shoe_size, shoe_price])
                break
            except Exception as ex:
                proxy = get_random_proxy()
                hdr = get_random_hdr()
                hhdr = hdr.strip();
                base_header["if-none-match"] = hhdr
                i = i + 1
                print("connection error...{}--->".format(i), ex)
        i = 0
        while resp.status_code != 200:
            try:
                print("price - response status_code", i)
                resp = requests.get(url, headers=base_header, proxies = proxy, verify = False)
                break
            except Exception as ex:
                proxy = get_random_proxy()
                hdr = get_random_hdr()
                hhdr = hdr.strip();
                base_header["if-none-match"] = hhdr
                i = i + 1
                print("response status_code error...{}--->".format(i), ex)
        try:

                data = json.loads(resp.content)['Product']['children']
                for each in data:
                    shoe_size = data[each]['shoeSize']
                    shoe_price = data[each]['market']['lowestAsk']
                    final_data.append([shoe_size, shoe_price])
                return final_data, proxy
        except:
                return None, proxy
        
            
        

    def get_brands(self, output_data):
        url = 'https://api.thesneakerdatabase.com/v1/brands'

        user_agent = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36'
                                    ' (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
        # Get the product data for the item.
        resp = requests.get(url, headers=user_agent)
        data = json.loads(resp.content)['results']
        
        return data



