from flask import request
from flask_restx import Resource, fields, Namespace
from product_db_model import ProductDbModel
from product_db_schema import ProductDbSchema
from marshmallow import ValidationError
from offers_client import off_cli
from auth_api import evaluate_token

product_ns = Namespace('product', description='Product related operations')
products_ns = Namespace('products', description='Products related operations')

product_schema = ProductDbSchema()
product_list_schema = ProductDbSchema(many=True)

product_body = {'name': fields.String('Name of the Product'),
                'description': fields.String('Description of the Product')}
product_body_res = {'prod_id': fields.Integer('Product ID'), 'name': fields.String('Product name'),
                    'description': fields.String('Product description')}

product_model = products_ns.model(name='Product', model=product_body)
product_model_res = products_ns.model(name='ProductWithId', model=product_body_res)


class Product(Resource):
    @staticmethod
    @product_ns.doc('Get a product')
    @product_ns.response(200, 'Ok', product_model_res)
    @product_ns.response(404, 'Product not found')
    @product_ns.response(500, 'Unexpected DB issue')
    def get(prod_id: int) -> "(str, int)":
        """
        Get a product
        """
        msg, auth_check = evaluate_token(request.headers.get('Bearer'))
        if auth_check != 200:
            return msg, auth_check
        status_code, product = ProductDbModel.find_by_id(prod_id)
        if status_code == 200:
            return product_schema.dump(product), status_code
        elif status_code == 404:
            return {'message': 'Product not found'}, status_code
        else:
            return {'message': 'Unexpected DB issue'}, status_code

    @staticmethod
    @product_ns.doc('Delete a product')
    @product_ns.response(200, 'Ok')
    @product_ns.response(404, 'Product not found')
    def delete(prod_id: int) -> "(str, int)":
        """
        Delete a product
        """
        msg, auth_check = evaluate_token(request.headers.get('Bearer'))
        if auth_check != 200:
            return msg, auth_check
        status_code, message = ProductDbModel.delete_by_id(prod_id)
        return {'message': message}, status_code

    @staticmethod
    @product_ns.doc('Update a product')
    @product_ns.response(200, 'Ok')
    @product_ns.response(404, 'Product not found')
    @product_ns.response(500, 'Unexpected DB issue')
    def patch(prod_id: int) -> "(str, int)":
        """
        Update a product
        """
        msg, auth_check = evaluate_token(request.headers.get('Bearer'))
        if auth_check != 200:
            return msg, auth_check
        status_code, product = ProductDbModel.find_by_id(prod_id)
        if status_code == 200:
            req_data = request.get_json()
            for key in list(req_data):
                if key not in product_body.keys():
                    # abort if attribute does not exist; alternatively delete it and let request process
                    return {'message': f'Attribute {key} is not present in the model.'}, 400
                    # del req_data[key]
            status_code, updated_product = product.update(request.get_json())
            return {'message': updated_product}, status_code
        elif status_code == 404:
            return {'message': 'Product not found'}, status_code
        else:
            return {'message': 'Unexpected DB issue'}, status_code


class ProductList(Resource):
    @staticmethod
    @products_ns.doc('Get all products')
    @products_ns.response(200, 'Ok', [product_model_res])
    def get() -> "(str, int)":
        """
        Get list of all products
        """
        msg, auth_check = evaluate_token(request.headers.get('Bearer'))
        if auth_check != 200:
            return msg, auth_check
        status_code, product_list = ProductDbModel.find_all()
        return product_list_schema.dump(product_list), status_code

    @products_ns.expect(product_model)
    @products_ns.doc('Create a product')
    @products_ns.response(200, 'Ok', product_model_res)
    @products_ns.response(400, 'Bad request')
    def post(self) -> "(str, int)":
        """
        Create a new product
        """
        msg, auth_check = evaluate_token(request.headers.get('Bearer'))
        if auth_check != 200:
            return msg, auth_check
        product_json = request.get_json()
        name = product_json['name']
        status_code, found_product = ProductDbModel.find_by_name_exact(name)
        if status_code == 200:
            return {'message': 'Product already exists'}, 400
        try:
            product_data = product_schema.load(product_json)
        except (ValidationError, ValueError) as e:
            return {'message': str(e)}, 400
        status_code, created_product = product_data.insert()
        off_cli.register_product(created_product)
        print(product_schema.dump(created_product))
        return product_schema.dump(created_product), status_code
