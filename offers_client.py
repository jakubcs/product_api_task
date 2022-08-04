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
        """
        Initialize OffersClient object that acts as a client to external offers API

        :raises KeyError: If authorization code for external API was not retrieved
        """
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
                print('Could not retrieve new authorization code.')
                raise e
        self.app = None

    def define_app_context(self, app: Flask):
        """
        Define app context for DB operations

        :param app: App used as context (Flask)
        """
        self.app = app

    def run(self, *args, **kwargs):
        """
        Thread function that periodically requests new offers for each product in product database.
        Offers that have at least one item in stock are then inserted to offer database
        """
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
                            offer_data.insert()
                    else:
                        print(f'Offers service request returned {response.status_code} status code!')
                print(self.exit_loop)
                time.sleep(1)

    def register_product(self, product: ProductDbModel) -> "bool":
        """
        Call to external API to register a new product

        :param product: json representation of the product (ProductDbModel)
        :returns: 'bool' representing the success of the operation
        """
        response = requests.post(self.base_url + '/products/register',
                                 headers={'Bearer': f'{self.auth_code}'},
                                 json=product_schema.dump(product), verify=False)
        return response.status_code == 201


off_cli = OffersClient()
