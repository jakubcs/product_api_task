import threading
import time
import requests
from product_db_model import ProductDbModel
from product_db_schema import ProductDbSchema

product_schema = ProductDbSchema()


class OffersClient(threading.Thread):
    def __init__(self, auth_code: str, base_url: str):
        super().__init__()
        self.exit_loop = False
        self.auth_code = auth_code
        self.base_url = base_url

    def run(self, *args, **kwargs):
        self.exit_loop = False
        while not self.exit_loop:
            response = requests.get(self.base_url + '/products/1/offers', headers={'Bearer': f'{self.auth_code}'},
                                    verify=False)
            print(response.json())
            time.sleep(5)

    def __del__(self):
        self.exit_loop = True

    def register_product(self, product: ProductDbModel):
        auth_str = f'Bearer {self.auth_code}'
        print(auth_str)
        response = requests.post(self.base_url + '/products/register',
                                 headers={'Bearer': f'{self.auth_code}'},
                                 json=product_schema.dump(product), verify=False)
        print(f'Response {response.status_code} - {response.reason} - {response.json()} - {response.request}')


off_cli = OffersClient(auth_code='4b049a77-b366-4e23-bdbf-1236d95c9a23',
                       base_url='https://applifting-python-excercise-ms.herokuapp.com/api/v1')
