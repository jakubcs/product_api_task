from flask import Flask, Blueprint
from flask_restx import Api
from flask_misc import fl_sql
from product_api import product_ns, products_ns, Product, ProductList
from offer_api import offers_ns, OfferList, ActiveOfferList, VendorOfferList, ProductOfferList, \
    ProductAndVendorOfferHistoryList
from auth_api import auth_ns, RequestToken
from product_db_model import ProductDbModel
import os

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

API_BASE_URL = 'http://localhost:5000/api'
API_TOKEN = 'very_secret_key'


# test product DB operations and also create a DB for further testing
def test_add_products():
    with app.app_context():
        apple = ProductDbModel(name='Apple', description='This is a red apple.')
        apple.insert()
        assert apple.prod_id == 1
        assert len(ProductDbModel.find_all()) == 1
        assert apple.insert()
        assert len(ProductDbModel.find_all()) == 1
        banana = ProductDbModel(name='Banana', description='This is a banana')
        banana.insert()
        assert banana.prod_id == 2
        assert len(ProductDbModel.find_all()) == 2
        assert ProductDbModel.find_by_id(apple.prod_id) == apple
        assert ProductDbModel.delete_by_id(1)
        assert ProductDbModel.find_by_id(apple.prod_id) is None
        assert len(ProductDbModel.find_all()) == 1
        apple = ProductDbModel(name='Apple', description='This is a red apple.')
        apple.insert()
        assert len(ProductDbModel.find_all()) == 2
        assert ProductDbModel.find_by_id(apple.prod_id) == apple
        assert apple.prod_id == 3
        apple.update({'description': 'This is a green apple'})
        assert ProductDbModel.find_by_id(apple.prod_id).description == 'This is a green apple'
        apple.update({'name': 'Orange', 'description': 'This is an orange', 'something_else': 'ignored'})
        orange = ProductDbModel.find_by_id(apple.prod_id)
        assert orange.name == 'Orange' and orange.description == 'This is an orange'
        assert ProductDbModel.find_by_name_exact('Orange') == orange


def test_product_api():
    app.testing = True
    client = app.test_client()
    response = client.get(API_BASE_URL + '/product')
    assert response.status_code == 404
    response = client.get(API_BASE_URL + '/products')
    assert response.status_code == 401
    response = client.get(API_BASE_URL + '/products', headers={'Bearer': API_TOKEN + 'wrong'})
    assert response.status_code == 403
    response = client.get(API_BASE_URL + '/products', headers={'Bearer': API_TOKEN})
    assert response.status_code == 200
    assert len(response.json) == 2
    for product in response.json:
        assert product['name'] != 'Apple'
    response = client.post(API_BASE_URL + '/products', headers={'Bearer': API_TOKEN},
                           json={'name': 'Watermelon', 'description': 'A big juicy watermelon'})
    assert response.status_code == 201
    w_id = response.json['prod_id']
    response = client.get(API_BASE_URL + f'/product/{w_id}', headers={'Bearer': API_TOKEN})
    assert response.status_code == 200
    assert response.json['name'] == 'Watermelon'
    response = client.patch(API_BASE_URL + f'/product/{w_id}', headers={'Bearer': API_TOKEN},
                            json={'description': 'Old watermelon'})
    assert response.status_code == 200
    assert response.json['description'] == 'Old watermelon'
    response = client.patch(API_BASE_URL + f'/product/{w_id}', headers={'Bearer': API_TOKEN},
                            json={'wrong': 'not_exists'})
    assert response.status_code == 400
    response = client.delete(API_BASE_URL + f'/product/{w_id}', headers={'Bearer': API_TOKEN})
    assert response.status_code == 204
    response = client.delete(API_BASE_URL + f'/product/{w_id}', headers={'Bearer': API_TOKEN})
    assert response.status_code == 200
