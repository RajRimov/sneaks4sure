from stockx import StockXAPI
from datetime import date
from pymongo import MongoClient
import threading
from sneaks_model import Sneak
# pprint library is used to make the output look more pretty
from pprint import pprint
import ssl

#check if the new styleId already exists in database
def alreadyExists(new_skuId):
    if collection.find({'product_sku_id': new_skuId}).count() > 0:
        return True
    else:
        return False


class scraperThread_stockx(threading.Thread):
    def __init__(self, brand_name, page_number, _proxy):
        threading.Thread.__init__(self)
        self.brand_name = brand_name
        self.page_number = page_number
        self._proxy = _proxy
    def run(self):
        # Get lock to synchronize threads
        threadLock.acquire()
        thread_for_eachPage(self.brand_name, self.page_number, self._proxy)
        # Free lock to release next thread
        threadLock.release()
    
def thread_for_eachPage(brand_name, page_number, _proxy):
    
    products, search_proxy = stockx.search_items(search_term=brand_name, output_data=['id', 'urlKey', 'styleId'], proxy = _proxy, page=page_number, max_searches=50)
    
    # Get the name, last sale price, and lowest ask from this id.
    if products is not None:
        for product_id in products:
            if alreadyExists(product_id['styleId']):
                print("already exist....")
                continue
            else:
                item_info, item_proxy = stockx.get_item_data(item_id=product_id['id'], proxy = search_proxy, output_data=['shoe','brand', 'productCategory', 
                'retailPrice', 'releaseDate', 'media', 'shortDescription', 'description','styleId',
                'colorway',['market', 'lastSale'],['media', '360'],['media', 'imageUrl'],['media', 'smallImageUrl'],['media', 'thumbUrl'],
                ['market', 'changeValue'], ['market', 'changePercentage']])
                #print(item_info)
                price_info, price_proxy = stockx.get_price_size(url_key=product_id['urlKey'], proxy  = item_proxy, output_data = [])
                #print(price_info)
                #check if the new sku_id
                if item_info is not None and 'styleId' in item_info:
                    if item_info['styleId'] != '':
                    # set the field parameter value for mongodb  
                        if price_info is not None:
                            stock_url = "https://stockx.com/" + product_id['urlKey']
                            sneaker_1.product_stock_url =   stock_url
                            sneaker_1.product_priceSize = price_info
                        else:
                            sneaker_1.product_stock_url =   "-"
                            sneaker_1.product_priceSize = "-"                                                          
                        if 'productCategory' in item_info:
                            sneaker_1.product_category = item_info["productCategory"]
                        else:
                            sneaker_1.product_category = ''
                        if 'shoe' in item_info:
                                sneaker_1.product_name = item_info["shoe"]
                        else:
                            sneaker_1.product_name = ''
                        if 'brand' in item_info:
                                sneaker_1.product_brand = item_info["brand"].upper()
                        else:
                            sneaker_1.product_brand = ''
                        if 'lastSale' in item_info:
                                sneaker_1.product_last_sale  = str(item_info['lastSale'])
                        else:
                            sneaker_1.product_last_sale = ''
                        if 'changeValue' in item_info:
                                sneaker_1.product_change_value = str(item_info['changeValue'])
                        else:
                            sneaker_1.product_change_value = ''
                        if 'changePercentage' in item_info:
                                sneaker_1.product_change_percentage = str(item_info['changePercentage'])
                        else:
                            sneaker_1.product_change_percentage = ''
                        if '360' in item_info:
                                sneaker_1.product_image_360 = item_info['360']
                            
                        else:
                            sneaker_1.product_image_url = ''
                        if 'imageUrl' in item_info:
                                sneaker_1.product_imageUrl = item_info['imageUrl']
                            
                        else:
                            sneaker_1.product_image_url = ''
                        if 'smallImageUrl' in item_info:
                                sneaker_1.product_smallImageUrl = item_info['smallImageUrl']
                            
                        else:
                            sneaker_1.product_image_url = ''
                        if 'thumbUrl' in item_info:
                                sneaker_1.product_thumbUrl = item_info['thumbUrl']
                            
                        else:
                            sneaker_1.product_image_url = ''
                    
                        if 'styleId' in item_info:
                                sneaker_1.product_style_id = item_info['styleId']
                                sneaker_1.product_sku_id = item_info['styleId']
                    
                        if 'colorway' in item_info:
                                sneaker_1.product_colorway = item_info["colorway"]
                        else:
                            sneaker_1.product_colorway = ''
                    
                        if 'retailPrice' in item_info:
                                sneaker_1.product_retail_price = str(item_info['retailPrice'])
                        else:
                            sneaker_1.product_retail_price = ''
                    
                        if 'releaseDate' in item_info:
                                sneaker_1.product_release_date = str(item_info['releaseDate'])
                        else:
                            sneaker_1.product_release_date = ''
                    
                        if 'description' in item_info:
                                sneaker_1.product_description = item_info["description"]
                        else:
                            sneaker_1.product_description = ''
                
                    collection.insert_one(sneaker_1.to_dict())
                    print("--------------------------success of adding the product---------------------------")
                else:
                    print("--------------------------failure of adding the product---------------------------")
                    continue
                _proxy = price_proxy
    else:
        print("search failure")
        return
def scraper_function():
    print("---------------------------------------------------------------------------")
    print("scrapping......")

    #---------------this is step code for initial scrapping.----------------- 
    for brand in brand_list:
        # iterate all of the 25 pages
        for page in range(25):
            #thread_for_eachPage(brand, page, _proxy)
            each_thread = scraperThread_stockx(brand, page, _proxy)
            each_thread.start()
            each_thread.join()

    print("finished the scrapping.....")
    print("---------------------------------------------------------------------------")

if __name__ == "__main__":

    # flag for updating the scraped data.
    try: 
        conn = MongoClient() 
        print("Connected successfully!!!") 
    except:   
        print("Could not connect to MongoDB") 

    sneaker_1 = Sneak()
    # database 
    db = conn.sneaks4sure 
    
    # Created or Switched to collection names: my_gfg_collection 
    collection = db.SneakersForPopular

    _proxy = {
        'http':'http://oliversulej3:guT0XPvk@194.135.18.42:32624',
        'https': 'https://oliversulej3:guT0XPvk@194.135.18.42:32624'                   
    }

    stockx = StockXAPI()
    threadLock = threading.Lock()
	
    # brand_list = []
    brand_list = stockx.get_brands(output_data = [])
    print(brand_list)
	
    scraper_function()

