import json

import pytest
from flask import Flask, Blueprint
from flask_restx import Api
from flask_misc import fl_sql
from product_api import product_ns, products_ns, Product, ProductList
from offer_api import offers_ns, OfferList, ActiveOfferList, VendorOfferList, ProductOfferList, \
    ProductAndVendorOfferHistoryList, offer_list_schema
from auth_api import auth_ns, RequestToken
from product_db_model import ProductDbModel
from offer_db_model import OfferDbModel
import os

API_BASE_URL = 'http://localhost:5000/api'
API_TOKEN = 'very_secret_key'


def run_app():
    if os.path.exists("data.db"):
        os.remove("data.db")

    app = Flask(__name__)
    bluePrint = Blueprint('api', __name__, url_prefix='/api')
    api = Api(bluePrint, doc='/doc', title='Sample Flask-RestPlus Application')
    app.register_blueprint(bluePrint)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True

    api.add_namespace(product_ns)
    api.add_namespace(products_ns)
    api.add_namespace(offers_ns)
    api.add_namespace(auth_ns)

    product_ns.add_resource(Product, '/<int:prod_id>')
    products_ns.add_resource(ProductList, '')
    offers_ns.add_resource(OfferList, '')
    offers_ns.add_resource(ActiveOfferList, '/active')
    offers_ns.add_resource(ProductOfferList, '/product/<int:prod_id>')
    offers_ns.add_resource(VendorOfferList, '/vendor/<int:vendor_id>')
    offers_ns.add_resource(ProductAndVendorOfferHistoryList, '/product/<int:prod_id>/vendor/<int:vendor_id>')
    auth_ns.add_resource(RequestToken, '')

    with app.app_context():
        fl_sql.init_app(app)
        fl_sql.create_all()

    return app


def test_add_single_product():
    app = run_app()
    with app.app_context():
        apple = ProductDbModel(name='Apple', description='This is a red apple.')
        assert apple.insert()
        assert apple.prod_id == 1
        assert len(ProductDbModel.find_all()) == 1


def test_add_product_with_same_name():
    app = run_app()
    with app.app_context():
        apple = ProductDbModel(name='Apple', description='This is a red apple.')
        assert apple.insert()
        another_apple = ProductDbModel(name='Apple', description='This is a green apple.')
        assert not another_apple.insert()
        assert len(ProductDbModel.find_all()) == 1


def test_add_product_with_same_description():
    app = run_app()
    with app.app_context():
        apple = ProductDbModel(name='Apple', description='This is a red apple.')
        assert apple.insert()
        another_apple = ProductDbModel(name='RedApple', description='This is a green apple.')
        assert another_apple.insert()
        assert another_apple.prod_id == 2
        assert len(ProductDbModel.find_all()) == 2


def test_find_existing_product():
    app = run_app()
    with app.app_context():
        apple = ProductDbModel(name='Apple', description='This is a red apple.')
        assert apple.insert()
        assert ProductDbModel.find_by_id(apple.prod_id) == apple
        assert ProductDbModel.find_by_name_exact(apple.name) == apple


def test_find_non_existing_product():
    app = run_app()
    with app.app_context():
        assert ProductDbModel.find_by_id(1) is None


def test_remove_existing_product():
    app = run_app()
    with app.app_context():
        apple = ProductDbModel(name='Apple', description='This is a red apple.')
        assert apple.insert()
        assert ProductDbModel.delete_by_id(apple.prod_id)
        assert ProductDbModel.find_by_id(apple.prod_id) is None


def test_remove_non_existing_product():
    app = run_app()
    with app.app_context():
        assert ProductDbModel.delete_by_id(1) is False


def test_update_product():
    app = run_app()
    with app.app_context():
        apple = ProductDbModel(name='Apple', description='This is a red apple.')
        assert apple.insert()
        assert apple.update({'name': 'Orange', 'description': 'This is an orange'})
        assert ProductDbModel.find_by_id(apple.prod_id).name == 'Orange'
        assert ProductDbModel.find_by_id(apple.prod_id).description == 'This is an orange'


def test_update_product_wrong_field():
    app = run_app()
    with app.app_context():
        apple = ProductDbModel(name='Apple', description='This is a red apple.')
        assert apple.insert()
        assert apple.update({'color': 'Red'})
        with pytest.raises(AttributeError):
            apple.color


def test_update_product_primary_key():
    app = run_app()
    with app.app_context():
        apple = ProductDbModel(name='Apple', description='This is a red apple.')
        assert apple.insert()
        assert apple.update({'prod_id': 2})
        assert ProductDbModel.find_by_id(2) == apple


def test_update_product_primary_key_to_existing_value():
    app = run_app()
    with app.app_context():
        apple = ProductDbModel(name='Apple', description='This is a red apple.')
        assert apple.insert()
        orange = ProductDbModel(name='Orange', description='This is an orange')
        assert orange.insert()
        assert apple.update({'prod_id': 2}) is False
        assert ProductDbModel.find_by_id(apple.prod_id) == apple


def test_find_all():
    app = run_app()
    with app.app_context():
        apple = ProductDbModel(name='Apple', description='This is a red apple.')
        assert apple.insert()
        orange = ProductDbModel(name='Orange', description='This is an orange')
        assert orange.insert()
        products = ProductDbModel.find_all()
        assert len(products) == 2
        assert products[0].name == 'Apple'
        assert products[1].name == 'Orange'


def test_product_api_not_found():
    app = run_app()
    app.testing = True
    client = app.test_client()
    with app.app_context():
        response = client.get(API_BASE_URL + '/product')
        assert response.status_code == 404


def test_unauthorized_api_request():
    app = run_app()
    app.testing = True
    client = app.test_client()
    with app.app_context():
        response = client.get(API_BASE_URL + '/products')
        assert response.status_code == 401


def test_unauthorized_api_request():
    app = run_app()
    app.testing = True
    client = app.test_client()
    with app.app_context():
        response = client.get(API_BASE_URL + '/products', headers={'Bearer': API_TOKEN + 'wrong'})
        assert response.status_code == 403


def test_api_create_product():
    app = run_app()
    app.testing = True
    client = app.test_client()
    with app.app_context():
        response = client.post(API_BASE_URL + '/products', headers={'Bearer': API_TOKEN},
                               json={'name': 'Watermelon', 'description': 'A big juicy watermelon'})
        assert response.status_code == 201


def test_api_retrieve_and_delete_product():
    app = run_app()
    app.testing = True
    client = app.test_client()
    with app.app_context():
        response = client.post(API_BASE_URL + '/products', headers={'Bearer': API_TOKEN},
                               json={'name': 'Watermelon', 'description': 'A big juicy watermelon'})
        w_id = response.json['prod_id']
        response = client.get(API_BASE_URL + f'/product/{w_id}', headers={'Bearer': API_TOKEN})
        assert response.status_code == 200
        assert response.json['name'] == 'Watermelon'
        response = client.delete(API_BASE_URL + f'/product/{w_id}', headers={'Bearer': API_TOKEN})
        assert response.status_code == 204
        response = client.delete(API_BASE_URL + f'/product/{w_id}', headers={'Bearer': API_TOKEN})
        assert response.status_code == 200
        assert response.json['message'] is not None
        response = client.get(API_BASE_URL + f'/product/{w_id}', headers={'Bearer': API_TOKEN})
        assert response.status_code == 200
        assert len(response.json) == 0


def test_api_patch_product():
    app = run_app()
    app.testing = True
    client = app.test_client()
    with app.app_context():
        response = client.post(API_BASE_URL + '/products', headers={'Bearer': API_TOKEN},
                               json={'name': 'Watermelon', 'description': 'A big juicy watermelon'})
        w_id = response.json['prod_id']
        response = client.patch(API_BASE_URL + f'/product/10', headers={'Bearer': API_TOKEN},
                                json={'description': 'Old watermelon'})
        assert response.status_code == 200
        assert len(response.json) == 0
        response = client.patch(API_BASE_URL + f'/product/{w_id}', headers={'Bearer': API_TOKEN},
                                json={'description': 'Old watermelon'})
        assert response.status_code == 200
        assert response.json['description'] == 'Old watermelon'
        response = client.patch(API_BASE_URL + f'/product/{w_id}', headers={'Bearer': API_TOKEN},
                                json={'description': 'Old watermelon', 'not_exist': 'wrong'})
        assert response.status_code == 400
        response = client.post(API_BASE_URL + '/products', headers={'Bearer': API_TOKEN},
                               json={'name': 'Apple', 'description': 'This is a big red apple.'})
        response = client.patch(API_BASE_URL + f'/product/{w_id}', headers={'Bearer': API_TOKEN},
                                json={'name': 'Apple'})
        assert response.status_code == 400


def test_offer_db_operation():
    app = run_app()
    with app.app_context():
        offer_inactive = OfferDbModel(vendor_id=1000, price=100, items_in_stock=10, prod_id=1)
        offer_unique = OfferDbModel(vendor_id=2000, price=200, items_in_stock=20, prod_id=2)
        offer_active = OfferDbModel(vendor_id=1000, price=300, items_in_stock=30, prod_id=1)
        assert offer_inactive.insert()
        assert offer_unique.insert()
        assert offer_inactive.active
        assert offer_unique.active
        assert offer_active.insert()
        assert not offer_inactive.active
        assert offer_active.active
        assert offer_inactive.product is None
        apple = ProductDbModel(name='Apple', description='This is a red apple.')
        assert apple.insert()
        assert offer_inactive.product == apple
        offers = OfferDbModel.find_all()
        assert len(offers)
        assert offers[0] == offer_inactive
        assert offers[2] == offer_active
        active_offers = [offer_unique, offer_active]
        same_product_and_vendor_offers = [offer_inactive, offer_active]
        assert OfferDbModel.find_by_prod_id(offer_inactive.prod_id) == same_product_and_vendor_offers
        assert OfferDbModel.find_by_vendor_id(offer_inactive.vendor_id) == same_product_and_vendor_offers
        assert len(OfferDbModel.find_by_prod_id(offer_inactive.prod_id + 100)) == 0
        assert len(OfferDbModel.find_by_vendor_id(offer_inactive.vendor_id + 100)) == 0
        assert OfferDbModel.find_by_prod_id_and_vendor_id_between_dates(prod_id=offer_inactive.prod_id,
                                                                        vendor_id=offer_inactive.vendor_id,
                                                                        date_start="0001-01-01T00:00:00.000000",
                                                                        date_end="3000-01-01T00:00:00.000000") \
               == same_product_and_vendor_offers
        assert len(OfferDbModel.find_by_prod_id_and_vendor_id_between_dates(prod_id=offer_inactive.prod_id,
                                                                            vendor_id=offer_inactive.vendor_id,
                                                                            date_start="3000-01-01T00:00:00.000000",
                                                                            date_end="0001-01-01T00:00:00.000000")) == 0
        assert OfferDbModel.find_all_active() == active_offers


def test_offer_api():
    app = run_app()
    app.testing = True
    client = app.test_client()
    with app.app_context():
        offer_inactive = OfferDbModel(vendor_id=1000, price=100, items_in_stock=10, prod_id=1)
        offer_unique = OfferDbModel(vendor_id=2000, price=200, items_in_stock=20, prod_id=2)
        offer_active = OfferDbModel(vendor_id=1000, price=300, items_in_stock=30, prod_id=1)
        offer_inactive.insert()
        offer_unique.insert()
        offer_active.insert()
        active_offers = [offer_unique, offer_active]
        same_product_and_vendor_offers = [offer_inactive, offer_active]
        offers = [offer_inactive, offer_unique, offer_active]
        response = client.get(API_BASE_URL + '/offers', headers={'Bearer': API_TOKEN})
        assert response.status_code == 200
        assert response.json == offer_list_schema.dump(offers)
        response = client.get(API_BASE_URL + '/offers/active', headers={'Bearer': API_TOKEN})
        assert response.status_code == 200
        assert response.json == offer_list_schema.dump(active_offers)
        response = client.get(API_BASE_URL + f'/offers/product/{offer_inactive.prod_id}', headers={'Bearer': API_TOKEN})
        assert response.status_code == 200
        assert response.json == offer_list_schema.dump(same_product_and_vendor_offers)
        response = client.get(API_BASE_URL + f'/offers/vendor/{offer_inactive.vendor_id}',
                              headers={'Bearer': API_TOKEN})
        assert response.status_code == 200
        assert response.json == offer_list_schema.dump(same_product_and_vendor_offers)
        response = client.post(
            API_BASE_URL + f'/offers/product/{offer_inactive.prod_id}/vendor/{offer_inactive.vendor_id}',
            json={'date_start': '0001-01-01T00:00:00.000000', 'date_end': '3000-01-01T00:00:00.000000'},
            headers={'Bearer': API_TOKEN})
        assert response.status_code == 200
        assert json.loads(response.json)['price_change'] == 200
