
import datetime, pyotp
import json, uuid, random, string
from mongoengine import Document
from mongoengine import DateTimeField, StringField, ReferenceField, ListField


class Sneak(Document):
    
    product_sku_id = StringField(max_length=100, required=True)
    product_category = StringField(max_length=100, required=True)
    product_name = StringField(max_length=100, required=True)
    product_brand = StringField(max_length=100, required=True)
    product_image_360 = StringField(max_length=100, required=True)
    product_imageUrl = StringField(max_length=100, required=True)
    product_smallImageUrl = StringField(max_length=100, required=True)
    product_thumbUrl = StringField(max_length=100, required=True)
    product_priceSize = StringField(max_length=100, required=True)
    product_stock_url = StringField(max_length=100, required=True)
    product_style_id = StringField(max_length=100, required=True)
    product_release_date = StringField(max_length=100, required=True)
    product_retail_price = StringField(max_length=100, required=True)
    product_colorway = StringField(max_length = 100, required = True)
    product_last_sale = StringField(max_length = 100, required = True)
    product_change_value = StringField(max_length = 100, required = True)
    product_change_percentage = StringField(max_length = 100, required = True)
    product_description = StringField(required=True)

    update_date = DateTimeField(required=True, default=datetime.datetime.now())

    @staticmethod
    def get_or_none(**filters):
        try:
            return Sneak.objects.get(**filters)
        except:
            return None

    @staticmethod
    def get_next_position(product_id):
        return Sneak.objects(sku_id=product_id).count()+1

    def to_dict(self):
        return dict(
                product_sku_id=self.product_sku_id,
                product_category=self.product_category,
                product_name=self.product_name,
                product_brand=self.product_brand,
                product_image_360 = self.product_image_360,
                product_imageUrl = self.product_imageUrl,
                product_smallImageUrl = self.product_smallImageUrl,
                product_thumbUrl = self.product_thumbUrl,
                product_priceSize = self.product_priceSize,
                product_stock_url = self.product_stock_url,
                product_style_id = self.product_style_id,
                product_release_date = self.product_release_date,
                product_colorway = self.product_colorway,
                product_last_sale = self.product_last_sale,
                product_change_value = self.product_change_value,
                product_change_percentage = self.product_change_percentage,
                product_description = self.product_description,
                update_date=self.update_date
            )

    def check_id(self, product_id):
        try:
            Sneak.objects(sku_id=product_id).first()
            return True
        except:
            return False