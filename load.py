
from pymongo import MongoClient


try: 
    conn = MongoClient() 
    print("Connected successfully!!!") 
except:   
    print("Could not connect to MongoDB") 
# database 
db = conn.sneaks4sure 
# Created or Switched to collection names
collection = db.Sneakers

for x in collection.find({}, {"_id":0}):  
    if 'product_name' not in x:
        collection.remove(x)
        print("deleted...")
print("all deleted....")
    