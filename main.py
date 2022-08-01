from flask import Flask, Blueprint, jsonify
from flask_restx import Api
from product_db_model import fl_sql, fl_mar
from product_api import product_ns, products_ns, Product, ProductList
from marshmallow import ValidationError

app = Flask(__name__)
bluePrint = Blueprint('api', __name__, url_prefix='/api')
api = Api(bluePrint, doc='/doc', title='Sample Flask-RestPlus Application')
app.register_blueprint(bluePrint)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

api.add_namespace(product_ns)
api.add_namespace(products_ns)

product_ns.add_resource(Product, '/<int:prod_id>')
products_ns.add_resource(ProductList, '')


@app.before_first_request
def create_tables():
    fl_sql.create_all()


@api.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify(error.messages), 400


if __name__ == '__main__':
    fl_sql.init_app(app)
    fl_mar.init_app(app)
    app.run(port=5000, debug=False, host='0.0.0.0')
