import threading
import time
import requests
from flask import Flask

from flask_misc import fl_sql
from product_db_model import ProductDbModel
from product_db_schema import ProductDbSchema
from offer_db_model import OfferDbModel
from offer_db_schema import OfferDbSchema
import os

product_schema = ProductDbSchema()
offer_schema = OfferDbSchema()


class OffersClient(threading.Thread):
    def __init__(self, auth_code: str):
        super().__init__()
        self.exit_loop = False
        self.auth_code = auth_code
        self.base_url = os.environ['OFFER_BASE_URL']
        self.app = None

    def define_app_context(self, app: Flask):
        self.app = app

    def run(self, *args, **kwargs):
        self.exit_loop = False
        with self.app.app_context():
            while not self.exit_loop:
                response = requests.get(self.base_url + '/products/1/offers', headers={'Bearer': f'{self.auth_code}'})
                if response.status_code == 200:
                    for item in response.json():
                        offer_data = OfferDbModel(vendor_id=item['id'], price=item['price'],
                                                  items_in_stock=item['items_in_stock'], prod_id=1)
                        if offer_data.items_in_stock == 0:
                            continue
                        query_sc, query_data = OfferDbModel.find_by_prod_and_vendor_id_active(prod_id=offer_data.prod_id,
                                                                                              vendor_id=offer_data.vendor_id)
                        # if another offer for the same product from the same vendor exists and is active, deactivate it
                        if query_data is not None:
                            setattr(query_data, 'active', False)
                            fl_sql.session.commit()
                        else:
                            status_code, created_offer = offer_data.insert()
                            if status_code != 200:
                                print(f'Could not insert offer = {offer_data.__repr__()}')
                else:
                    print(f'Offers service request returned {response.status_code} status code!')
                time.sleep(30)

    def __del__(self):
        self.exit_loop = True

    def register_product(self, product) -> "str":
        auth_str = f'Bearer {self.auth_code}'
        # print(auth_str)
        response = requests.post(self.base_url + '/products/register',
                                 headers={'Bearer': f'{self.auth_code}'},
                                 json=product_schema.dump(product), verify=False)
        return response.json()


off_cli = OffersClient(auth_code='4b049a77-b366-4e23-bdbf-1236d95c9a23')
