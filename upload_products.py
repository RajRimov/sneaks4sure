
import sys
sys.path.append("C:\Sneaks4Sure\Scrapper\my_env\Lib\site-packages")
import datetime
from woocommerce import API
import requests
from pymongo import MongoClient
import json

wcapi = API(
    url="https://www.sneaks4sure.com",
    consumer_key="ck_222316c0d91a574dfd04cb2925b9d7d8e219d1f4",
    consumer_secret="cs_8eff2c58867228d9f2e326b9e236a690dbf3a962",
    wp_api=True,
    version="wc/v3"
)
category_index = {
    "ASICS": 58,
    "CONVERSE": 56,
    "JORDAN":47,
    "NEW BALANCE":60,
    "PUMA":48,
    "REEBOK":64,
    "SAUCONY":59,
    "UNDER ARMOUR":69,
    "VANS":57,
    "YEEZY":67,
    "ADIDAS":46,
    "NIKE":23
}

url = "https://www.sneaks4sure.com/wp-json/wc/v3/products?consumer_key=ck_222316c0d91a574dfd04cb2925b9d7d8e219d1f4&consumer_secret=cs_8eff2c58867228d9f2e326b9e236a690dbf3a962"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'authorization': 'Basic YWRtaW46YWRtaW4yMDIwISE='}
image_url = "https://www.sneaks4sure.com/wp-json/wp/v2/media"
image_headers = {'Content-type': 'image/jpg', 'authorization': 'Basic YWRtaW46YWRtaW4yMDIwISE='}

def get_all_fieldsName(sku_id):
    field_name = []
    
    cursor = collection.find_one({"product_sku_id": sku_id})
    for document in cursor: 
        field_name.append(document) 
    return field_name
def get_price_size_item(sku_id):
    fields = []
    price_fields = []
    url_fields = []
    fields =  get_all_fieldsName(sku_id)
    for s in fields:
        if 'price' in s: 
            price_fields.append(s)
        if 'url'  in s:
            if 'image_url' in s:
                continue
            url_fields.append(s)
    count = sum('price' in s for s in fields)
    return count, price_fields, url_fields

def get_imageId(image_arr = []):
    res = requests.post(image_url, data=json.dumps(image_arr), headers=image_headers)
    print (res.json())

def all_products_load(sku_id):
    cursor_list = collection.find({'product_sku_id': {'$regex':sku_id}})
    for product in cursor_list:  
        p_name = product['product_name']
        p_description = product['product_description']
        p_sku = product['product_sku_id']
        # register the uploading result in database for uploading result
        # if 'upload_flag' in product and product['upload_flag'] is True:
        #     continue
        # else:
        #     collection.update_one({'product_sku_id': product['product_sku_id']}, {'$set':{"upload_flag":True}})
        p_colorway = product['product_colorway']
        p_releaseDate = product['product_release_date']
        if p_releaseDate != '':
            date_time_obj = datetime.datetime.strptime(p_releaseDate, '%Y-%m-%d')
            timestampStr = date_time_obj.strftime("%Y, %b. %d")
        else:
            timestampStr = ''
        if "now available on StockX." in p_description:
            newp_description = p_description.replace("now available on StockX.", "now available on market")
        else:
            newp_description = p_description
        p_shortDescription = "<p>" + newp_description + "</p><ul><li>SKU : " + p_sku + "</li><li>Release date : " + timestampStr + "</li><li>Colorway : " + p_colorway + "</li></ul>"
        p_regular_price = product['product_last_sale']
        p_categories = product['product_brand']
        p_categories_id = category_index[p_categories]
        # p_image = product['product_image_url']
        images_360view = product['product_image_360']
        image_big = product['product_imageUrl']
        image_small = product['product_smallImageUrl']
        image_thumb = product['product_thumbUrl']
        
        total_price_type, price_size_list, url_fields_list = get_price_size_item(p_sku)
        images_array = []
        meta_data_array = []
        website_list = []
        exist_priceSiz_list = []
        exist_url_list = []
        for url_field in url_fields_list:
            url_value = product[url_field]
            if "https://" in url_value:
                str_field = url_field.split('_')
                website_list.append(str_field[1])
            else:
                 continue

        for price_field in price_size_list:
            price_value = product[price_field]
            if price_value != '-':
                exist_priceSiz_list.append(price_field)
            else:
                 continue
        for url_field in url_fields_list:
            url_value = product[url_field]
            if "https://" in url_value:
                exist_url_list.append(url_field)
            else:
                 continue
        # get the meta data
        count_priceSize = 0
        options_size_array = []
        shops_array = []
        for brand_type in range(len(exist_priceSiz_list)):
            size_price = []
            website_name = website_list[brand_type]
            if website_name == 'stock':
                website_name = 'stockx'
            if website_name == 'flight':
                website_name = "fightclub"
            if website_name == 'withenew':
                website_name = 'wethenew'
            if website_name == 'HeatSneakers':
                website_name = 'heatstocks'
            size_price = product[exist_priceSiz_list[brand_type]]
            shops_array.append(website_name.lower())
            if size_price == '-':
                continue
            length_meta = len(size_price)
            website_url = product[exist_url_list[brand_type]]
            
            # for each brand.
            for meta_index in range(length_meta):
                _size = size_price[meta_index][0]
                if 'US' in str(_size):
                    str_size = str(_size).replace('US', '').strip()
                else:
                    str_size = _size
                
                option_size = "US " + str(str_size)
                options_size_array.append(option_size)
                price = size_price[meta_index][1]
                if '$' in str(price):
                    str_price = price.replace('$', '').strip()
                elif '.0' in str(price):
                    str_price = str(price).replace('.0', '').strip()
                elif '.' in str(price):
                    str_price = str(price).replace('.', '').strip()
                elif 'в‚¬' in str(price):
                    str_price = str(price).replace('в‚¬', '').strip()
                elif '€' in str(price):
                    str_price = str(price).replace('€', '').strip()
                else:
                    str_price = str(price)
                per_meta = []
                per_meta = [
                    {
                        "key": "sizes_" + str(count_priceSize) +"_currency",
                        "vlaue": "us"
                    },
                    {
                        "key": "_sizes_" + str(count_priceSize) +"_currency",
                        "value": "field_5f55e29250d3c"
                    },
                    {
                        "key": "sizes_" + str(count_priceSize) + "_brand",
                        "value": ""
                    },
                    {
                        "key": "_sizes_" + str(count_priceSize) + "_brand",
                        "value": "field_5f55e25d50d3b"
                    },
                    {
                        "key": "sizes_" + str(count_priceSize) + "_size",
                        "value": str_size
                    },
                    {
                        "key": "_sizes_" + str(count_priceSize) + "_size",
                        "value": "field_5f55e20d50d38"
                    },
                    {
                        "key": "sizes_" + str(count_priceSize) + "_price",
                        "value": str_price
                    },
                    {
                        "key": "_sizes_" + str(count_priceSize) + "_price",
                        "value": "field_5f55e23750d39"
                    },
                    {
                        "key": "sizes_"+ str(count_priceSize) +"_product_url",
                        "value": website_url
                    },
                    {
                        "key": "_sizes_"+ str(count_priceSize) +"_product_url",
                        "value": "field_5f55ef68aafaa"
                    },
                    {
                        "key": "sizes_" + str(count_priceSize) + "_brand_name",
                        "value": website_name.lower()
                    },
                    {
                        "key": "_sizes_" + str(count_priceSize) + "_brand_name",
                        "value": "field_5f55ef40aafa9"
                    }
                    
                ]
                count_priceSize = count_priceSize + 1
                meta_data_array.extend(per_meta)
        # set the post view
        post_view = [
            {
                "key": "sizes",
                "value": str(count_priceSize)
            },
            {
                "key": "_sizes",
                "value": "field_5f55e1f250d37"
            }
            
        ]
        
        meta_data_array.extend(post_view)
        # if product has 360views
        if len(images_360view) != 0:
            has360_views = True
            index_list = list(range(0, len(images_360view)))
            for index in index_list:
                image_per360 = {
                    # "id": 22505,
                    "src": images_360view[index],
                    "name": p_name.replace(" ", '-') + str("{:02}".format(index)) + ".jpg",
                    "alt":""
                }
                images_array.append(image_per360)
        else:
            has360_views = False
            i_array = [image_big,image_thumb, image_small]
            for index in range(len(i_array)):
                image_perPro = {
                    # "id": 22505,
                    "src": i_array[index],
                    "name": p_name.replace(" ", '-') + str("{:02}".format(index)) + ".jpg",
                    "alt":""
                }
                images_array.append(image_perPro)
        option_list = list(dict.fromkeys(options_size_array))   
        data = {
            "name": p_name,
            "status": "publish",
            "catalog_visibility": "visible",
            "description": p_description,
            "short_description": p_shortDescription,
            "sku": p_sku,
            "price": p_regular_price,
            "regular_price": p_regular_price,
            "stock_status": "instock",
            "tax_status": "taxable",
            "categories": [
                {
                    "id": p_categories_id,
                    "name": p_categories,
                    "slug": p_categories
                }
            ],
            "images": images_array,
            "attributes": [
                {
                    "id": 2,
                    "name": "us",
                    "visible": True,
                    "slug": "us",
                    "variation": False,
                    "position": 0,
                    "type": "select",
                    "has_archives": True,
                    "options": option_list
                },
                {
                    "id": 1,
                    "name": "material",
                    "visible": True,
                    "variation": False,
                    "position": 1,
                    "options": shops_array
                }
            ],
        "default_attributes": [],
        "variations": [],
        "grouped_products": [],
        "menu_order": 0,
        "meta_data": meta_data_array
        }
        # send the create request of product in server.
        res = requests.post(url, data=json.dumps(data), headers=headers)
        # print(res.content)
        if res.status_code == 201:
            if has360_views:
                json_data = json.loads(res.text)
                product_id = json_data['id']
                attri_id = json_data['attributes'][0]['id']
                attri_pos = json_data['attributes'][0]['position']
                images_id = []
                id_str = ''
                for image in json_data['images']:
                    id = image['id']
                    images_id.append(id)
                    if id_str == '':
                        temp_str = str(id)     
                    else:
                        temp_str = id_str + "," + str(id) 
                    id_str = temp_str
                
                value_magic = "{\"images_ids\":["+ id_str + "], " + "\"options\":{\"checked\":false,\"columns\":" + str(len(images_id)) + ",\"set_columns\":false}}"
                data = {
                    "meta_data":[
                        {
                            "key": "_magic360_data",
                            "value": value_magic
                        }
                    ],
                    
                    "_links": {
                            "self": [
                                {
                                    "href": "https://www.sneaks4sure.com/wp-json/wc/v3/products/" + str(product_id)
                                }
                            ],
                            "collection": [
                                {
                                    "href": "https://www.sneaks4sure.com/wp-json/wc/v3/products"
                                }
                            ]
                    }
                }
                put_url = "https://www.sneaks4sure.com/wp-json/wc/v3/products/{}?consumer_key=ck_222316c0d91a574dfd04cb2925b9d7d8e219d1f4&consumer_secret=cs_8eff2c58867228d9f2e326b9e236a690dbf3a962".format(product_id) 
                res = requests.put(put_url, data=json.dumps(data), headers=headers)
            else:
                continue
            # print (res.json())
            print(res.status_code)
        elif res.status_code == 400:
            print("product already exist..., so only update the price-size information")
            json_data = json.loads(res.text)
            if 'resource_id' in json_data['data']:
                product_id = json_data['data']['resource_id']
                data = {
                    "name": p_name,
                    "meta_data":meta_data_array,
                    "regular_price": p_regular_price,
                    "_links": {
                                "self": [
                                    {
                                        "href": "https://www.sneaks4sure.com/wp-json/wc/v3/products/" + str(product_id)
                                    }
                                ],
                                "collection": [
                                    {
                                        "href": "https://www.sneaks4sure.com/wp-json/wc/v3/products"
                                    }
                                ]
                        }
                }
                put_url = "https://www.sneaks4sure.com/wp-json/wc/v3/products/{}?consumer_key=ck_222316c0d91a574dfd04cb2925b9d7d8e219d1f4&consumer_secret=cs_8eff2c58867228d9f2e326b9e236a690dbf3a962".format(product_id) 
                res = requests.put(put_url, data=json.dumps(data), headers=headers)
            else:
                continue


if __name__ == "__main__":
    
    # flag for updating the scraped data.
    try: 
        conn = MongoClient() 
        print("Connected successfully!!!") 
    except:   
        print("Could not connect to MongoDB") 
    # database 
    db = conn.sneaks4sure 
    # Created or Switched to collection names
    collection = db.Sneakers
    sku_id = sys.argv[1]
    # sku_id = "CD0461-046"
    # upper_brand = "ASICS"
    all_products_load(sku_id)