import sys
sys.path.append("C:\Sneaks4Sure\Scrapper\my_env\Lib\site-packages")
from pymongo import MongoClient
import subprocess
import threading
import time
from subprocess import Popen, PIPE

def start_scraping(shops_list, sku_id):
    #currency_rate = get_realtime_currencyFromUSD_toEuro()
    # select the shops for scraping...
    shop_path = "C:\\Sneaks4Sure\\Scrapper\\"
    start_time = time.time()
    cmds_list = [['python', shop_path + shop + "_update.py", sku_id] for shop in shops_list]
    procs_list = [Popen(cmd, stdout=PIPE, stderr=PIPE) for cmd in cmds_list]
    for proc in procs_list:
        proc.wait()
    # start scraping from the goat site
    # cmd = ['python', "goat_update.py", sku_id]
    # goat_proc = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    # goat_proc.wait()
    print("Scraping Finishhed....")

    # upload the updated product....
    cmd = ['python', "upload_products.py", sku_id]
    upload_proc = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    upload_proc.wait()
    collection.update_one({'product_sku_id': sku_id}, {'$set':{"upload":True}})
    print("Uploaded....")
    print("--- %s seconds ---" % (time.time() - start_time))

class scraperThread(threading.Thread):
     def __init__(self, _styleId, _shops_list):
         threading.Thread.__init__(self)
         self._styleId = _styleId
         self._shops_list = _shops_list
     def run(self):
         # Get lock to synchronize threads
         threadLock.acquire()
         start_scraping(self._shops_list, self._styleId)
         # Free lock to release next thread
         threadLock.release()

if __name__ == "__main__":
    # brand_list = []
    print("---------------------------------------Start the scraping-------------------------------------")
    shop_list = []
    shop_file = "C:\\Users\\Administrator\\Desktop\\shops.txt"
    try:
        with open(shop_file) as f:
            lines = f.readlines()
            for shop in lines:
                print(shop)
                shop_list.append(shop.strip())
    except Exception as ex:
        print(str(ex))
    try: 
        conn = MongoClient() 
        print("Connected successfully!!!") 
    except:   
        print("Could not connect to MongoDB") 
    # database 
    db = conn.sneaks4sure 
    
    # Created or Switched to collection names: my_gfg_collection 
    collection = db.Sneakers
    cursor = collection.find(no_cursor_timeout=True)

    cursor_list = [document for document in cursor]
    threadLock = threading.Lock()
    # start_scraping(shops, "CD0461-046")
    i = 0
    while True:
        try:
            start_time = time.time()
            for product in cursor_list:
                i = i + 1
                sku_id = product['product_sku_id']
                print(sku_id, i)
                start_scraping(shop_list, sku_id)
            total_time = time.time() - start_time
            print("--- %s seconds ---" % (time.time() - start_time))
            if i == 925 or total_time == 0.0:
                # cursor_list = collection.find({})
                break
                i = 0
        except Exception as ex:
            print("Exception happened....", ex)
            continue
        
    sys.exit(0)
            

