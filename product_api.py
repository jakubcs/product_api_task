from flask import request
from flask_restx import Resource, fields, Namespace
from sqlalchemy.exc import MultipleResultsFound
from product_db_model import ProductDbModel
from product_db_schema import ProductDbSchema
from marshmallow import ValidationError
from offers_client import off_cli
from auth_api import evaluate_token
from flask_misc import RESPONSE200, RESPONSE201, RESPONSE204, RESPONSE400, RESPONSE401, RESPONSE403, RESPONSE500

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
    @product_ns.response(200, RESPONSE200, product_body_res)
    @product_ns.response(401, RESPONSE401)
    @product_ns.response(403, RESPONSE403)
    @product_ns.response(500, RESPONSE500)
    def get(prod_id: int) -> "(str, int)":
        """
        Get a product
        """
        msg, auth_check = evaluate_token(request.headers.get('Bearer'))
        if auth_check != 200:
            return {'message': msg}, auth_check
        try:
            product = ProductDbModel.find_by_id(prod_id)
        except MultipleResultsFound:
            return {'message': RESPONSE500}, 500

        return product_schema.dump(product), 200

    @staticmethod
    @product_ns.doc('Delete a product')
    @product_ns.response(200, RESPONSE200)
    @product_ns.response(204, RESPONSE204)
    @product_ns.response(401, RESPONSE401)
    @product_ns.response(403, RESPONSE403)
    def delete(prod_id: int) -> "(str, int)":
        """
        Delete a product
        """
        msg, auth_check = evaluate_token(request.headers.get('Bearer'))
        if auth_check != 200:
            return {'message': msg}, auth_check
        is_deleted = ProductDbModel.delete_by_id(prod_id)
        if is_deleted:
            return {'message': RESPONSE204}, 204
        else:
            return {'message': f'No product with prod_id={prod_id} was found and therefore was not deleted'}, 200

    @staticmethod
    @product_ns.doc('Update a product')
    @product_ns.response(200, RESPONSE200, product_body_res)
    @product_ns.response(400, RESPONSE400)
    @product_ns.response(401, RESPONSE401)
    @product_ns.response(403, RESPONSE403)
    @product_ns.response(500, RESPONSE500)
    def patch(prod_id: int) -> "(str, int)":
        """
        Update a product
        """
        msg, auth_check = evaluate_token(request.headers.get('Bearer'))
        if auth_check != 200:
            return {'message': msg}, auth_check
        try:
            product = ProductDbModel.find_by_id(prod_id)
        except MultipleResultsFound:
            return {'message': RESPONSE500}, 500

        if product is None:
            return product_schema.dump(product), 200
        else:
            req_data = request.get_json()
            for key in list(req_data):
                if key not in product_body.keys():
                    # abort if attribute does not exist; alternatively delete it and let request process
                    return {'message': f'Attribute {key} is not present in the model.'}, 400
                    # del req_data[key]
            is_updated = product.update(request.get_json())
            if not is_updated:
                return {'message': 'Internal server error'}, 500
            return product_schema.dump(product), 200


class ProductList(Resource):
    @staticmethod
    @products_ns.doc('Get all products')
    @products_ns.response(200, RESPONSE200, [product_model_res])
    @products_ns.response(401, RESPONSE401)
    @products_ns.response(403, RESPONSE403)
    def get() -> "(str, int)":
        """
        Get list of all products
        """
        msg, auth_check = evaluate_token(request.headers.get('Bearer'))
        if auth_check != 200:
            return {'message': msg}, auth_check
        product_list = ProductDbModel.find_all()
        return product_list_schema.dump(product_list), 200

    @products_ns.expect(product_model)
    @products_ns.doc('Create a product')
    @products_ns.response(201, RESPONSE201, product_model_res)
    @products_ns.response(400, RESPONSE400)
    @products_ns.response(401, RESPONSE401)
    @products_ns.response(403, RESPONSE403)
    @products_ns.response(500, RESPONSE500)
    def post(self) -> "(str, int)":
        """
        Create a new product
        """
        msg, auth_check = evaluate_token(request.headers.get('Bearer'))
        if auth_check != 200:
            return {'message': msg}, auth_check
        product_json = request.get_json()
        name = product_json['name']
        try:
            found_product = ProductDbModel.find_by_name_exact(name)
        except MultipleResultsFound:
            return {'message': RESPONSE500}, 500

        if found_product is not None:
            return {'message': 'Product with a same name already exists.'}, 400

        try:
            product_data = product_schema.load(product_json)
        except (ValidationError, ValueError) as e:
            return {'message': str(e)}, 400

        is_created = product_data.insert()
        if not is_created:
            return {'message': 'Internal server error'}, 500
        off_cli.register_product(product_data)
        return product_schema.dump(product_data), 201
