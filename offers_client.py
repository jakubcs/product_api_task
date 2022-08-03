import threading
import time
import requests
import sqlalchemy.exc
from flask import Flask
from product_db_schema import ProductDbSchema
from offer_db_model import OfferDbModel
from offer_db_schema import OfferDbSchema
from product_db_model import ProductDbModel
import os

product_schema = ProductDbSchema()
offer_schema = OfferDbSchema()


class OffersClient(threading.Thread):
    def __init__(self):
        super().__init__()
        self.exit_loop = False
        self.base_url = os.environ['OFFER_BASE_URL']
        try:
            self.auth_code = os.environ['OFFER_AUTH_CODE']
        except KeyError as e:
            print('Requesting new authorization code.')
            response = requests.get(self.base_url + '/auth')
            if response.status_code == 201:
                self.auth_code = response.json()
            else:
                print('Could not request new authorization code.')
                raise e
        self.app = None

    def define_app_context(self, app: Flask):
        self.app = app

    def run(self, *args, **kwargs):
        self.exit_loop = False
        with self.app.app_context():
            while not self.exit_loop:
                try:
                    product_list = ProductDbModel.find_all()
                except sqlalchemy.exc.OperationalError:
                    time.sleep(1)
                    continue
                for product in product_list:
                    product_id = product.prod_id
                    response = requests.get(self.base_url + f'/products/{product_id}/offers',
                                            headers={'Bearer': f'{self.auth_code}'})
                    if response.status_code == 200:
                        for item in response.json():
                            offer_data = OfferDbModel(vendor_id=item['id'], price=item['price'],
                                                      items_in_stock=item['items_in_stock'], prod_id=product_id)
                            if offer_data.items_in_stock == 0:
                                continue
                            query_data = OfferDbModel.find_by_prod_and_vendor_id_active(
                                prod_id=offer_data.prod_id, vendor_id=offer_data.vendor_id)
                            # same product from the same vendor exists and is active? deactivate it
                            if query_data is not None:
                                # unless it has the same price and items in stock -> we don't need duplicates
                                if query_data.price != offer_data.price or \
                                        query_data.items_in_stock != offer_data.items_in_stock:
                                    print(f'Deactivate: {query_data}')
                                    setattr(query_data, 'active', False)
                                    is_inserted = offer_data.insert()
                                    if not is_inserted:
                                        print(f'Could not insert offer = {offer_data.__repr__()}')
                            else:
                                is_inserted = offer_data.insert()
                                if not is_inserted:
                                    print(f'Could not insert offer = {offer_data.__repr__()}')
                    else:
                        print(f'Offers service request returned {response.status_code} status code!')
                time.sleep(30)

    def __del__(self):
        self.exit_loop = True

    def register_product(self, product) -> "str":
        response = requests.post(self.base_url + '/products/register',
                                 headers={'Bearer': f'{self.auth_code}'},
                                 json=product_schema.dump(product), verify=False)
        return response.json()


off_cli = OffersClient()
