import json
from flask import request
from flask_restx import Resource, fields, Namespace
from offer_db_model import OfferDbModel
from offer_db_schema import OfferDbSchema
from auth_api import evaluate_token
from flask_misc import RESPONSE200, RESPONSE401, RESPONSE403

# Define namespace and relevant models
offers_ns = Namespace('offers', description='Offers related operations')
offer_list_schema = OfferDbSchema(many=True)
offer_body_res = {'internal_id': fields.Integer('Offer ID'), 'vendor_id': fields.Integer('Vendor ID'),
                  'price': fields.Integer('Offer price'), 'items_in_stock': fields.Integer('Number of available items'),
                  'active': fields.Boolean('Is offer active?'),
                  'date_created': fields.DateTime('Datetime of offer registration'),
                  'prod_id': fields.Integer('ID of the offered product')}
price_history_body = {'prod_id': fields.Integer('Product ID'), 'vendor_id': fields.Integer('Vendor ID'),
                      'price_change': fields.Float('Percentual change in price from start to end date'),
                      'history': fields.List(fields.Nested(offers_ns.model(name='PriceHistoryItem',
                                                                           model={'price': fields.Integer('price'),
                                                                                  'date_created': fields.DateTime(
                                                                                      'date_created')})))}
date_interval_body = {'date_start': fields.DateTime('Start of the date interval'),
                      'date_end': fields.DateTime('End of the date interval')}
offer_model_res = offers_ns.model(name='Offer', model=offer_body_res)
price_history_model = offers_ns.model(name='PriceHistoryId', model=price_history_body)
date_interval_item = offers_ns.model(name='DateIntervalItem', model=date_interval_body)


# Define resource classes to be registered to namespace
class OfferList(Resource):
    @staticmethod
    @offers_ns.doc('Get all offers')
    @offers_ns.response(200, RESPONSE200, [offer_model_res])
    @offers_ns.response(401, RESPONSE401)
    @offers_ns.response(403, RESPONSE403)
    def get() -> "(str, int)":
        """
        Get list of all offers

        :returns:
            - info - 'str' json containing list of offers or 'message' info if not successful
            - sc - 'int' representing HTTP status code
        """
        msg, auth_check = evaluate_token(request.headers.get('Bearer'))
        if auth_check != 200:
            return {'message': msg}, auth_check
        offer_list = OfferDbModel.find_all()
        return offer_list_schema.dump(offer_list), 200


class ActiveOfferList(Resource):
    @staticmethod
    @offers_ns.doc('Get all active offers')
    @offers_ns.response(200, RESPONSE200, [offer_model_res])
    @offers_ns.response(401, RESPONSE401)
    @offers_ns.response(403, RESPONSE403)
    def get() -> "(str, int)":
        """
        Get list of all active offers

        :returns:
            - info - 'str' json containing list of offers or 'message' info if not successful
            - sc - 'int' representing HTTP status code
        """
        msg, auth_check = evaluate_token(request.headers.get('Bearer'))
        if auth_check != 200:
            return {'message': msg}, auth_check
        offer_list = OfferDbModel.find_all_active()
        return offer_list_schema.dump(offer_list), 200


class VendorOfferList(Resource):
    @staticmethod
    @offers_ns.doc('Get all offers by vendor ID')
    @offers_ns.response(200, RESPONSE200, [offer_model_res])
    @offers_ns.response(401, RESPONSE401)
    @offers_ns.response(403, RESPONSE403)
    def get(vendor_id: int) -> "(str, int)":
        """
        Get list of all offers for given vendor ID

        :param vendor_id: Vendor ID used for searching offers (int)
        :returns:
            - info - 'str' json containing list of offers or 'message' info if not successful
            - sc - 'int' representing HTTP status code
        """
        msg, auth_check = evaluate_token(request.headers.get('Bearer'))
        if auth_check != 200:
            return {'message': msg}, auth_check
        offer_list = OfferDbModel.find_by_vendor_id(vendor_id)
        return offer_list_schema.dump(offer_list), 200


class ProductOfferList(Resource):
    @staticmethod
    @offers_ns.doc('Get all offers by product ID')
    @offers_ns.response(200, RESPONSE200, [offer_model_res])
    @offers_ns.response(401, RESPONSE401)
    @offers_ns.response(403, RESPONSE403)
    def get(prod_id: int) -> "(str, int)":
        """
        Get list of all offers for given product ID

        :param prod_id: Product ID used for searching offers (int)
        :returns:
            - info - 'str' json containing list of offers or 'message' info if not successful
            - sc - 'int' representing HTTP status code
        """
        msg, auth_check = evaluate_token(request.headers.get('Bearer'))
        if auth_check != 200:
            return {'message': msg}, auth_check
        offer_list = OfferDbModel.find_by_prod_id(prod_id)
        return offer_list_schema.dump(offer_list), 200


class PriceHistoryItem:
    def __init__(self, price: int, date_created: str):
        """
        Initialize PriceHistoryItem used for creating price history

        :param price: Offer's price (int)
        :param date_created: Date when offer was registered (str)
        """
        self.price = price
        self.date_created = date_created

    def to_json(self) -> "str":
        """
        Convert PriceHistoryItem to json

        :returns: 'str' json representation of PriceHistoryItem
        """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


class PriceHistory:
    def __init__(self, prod_id: int, vendor_id: int, history: [PriceHistoryItem]):
        """
        Initialize PriceHistory used as a representation of price history

        :param prod_id: Offered product ID (int)
        :param vendor_id: Offer's vendor ID (int)
        :param history: Price history ([PriceHistoryItem])
        """
        self.prod_id = prod_id
        self.vendor_id = vendor_id
        self.history = history
        self.price_change = 0

    def to_json(self):
        """
        Convert PriceHistory to json

        :returns: 'str' json representation of PriceHistory
        """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


class ProductAndVendorOfferHistoryList(Resource):
    @staticmethod
    @offers_ns.expect(date_interval_item)
    @offers_ns.doc('Get the price history of a product for specific vendor')
    @offers_ns.response(200, RESPONSE200, price_history_model)
    @offers_ns.response(401, RESPONSE401)
    @offers_ns.response(403, RESPONSE403)
    def post(prod_id: int, vendor_id: int) -> "(str, int)":
        """
        Get price history of a specific product offered by a specific vendor

        :param prod_id: Product ID (int)
        :param vendor_id: Vendor ID (int)
        :returns:
            - info - 'str' json containing price history or 'message' info if not successful
            - sc - 'int' representing HTTP status code
        """
        msg, auth_check = evaluate_token(request.headers.get('Bearer'))
        if auth_check != 200:
            return {'message': msg}, auth_check
        date_interval_json = request.get_json()
        date_start = date_interval_json['date_start']
        date_end = date_interval_json['date_end']
        offer_list = OfferDbModel.find_by_prod_id_and_vendor_id_between_dates(prod_id, vendor_id, date_start, date_end)
        if len(offer_list) == 0:
            price_history = PriceHistory(prod_id=prod_id, vendor_id=vendor_id, history=[])
            return price_history.to_json(), 200

        # if offers were found for a given product and vendor ID, create a price history and calculate price change
        price_history_data = []
        for offer in offer_list:
            price_history_data.append(PriceHistoryItem(price=offer.price, date_created=str(offer.date_created)))
        price_history = PriceHistory(prod_id=prod_id, vendor_id=vendor_id, history=price_history_data)
        if offer.price < offer_list[0].price:
            price_history.price_change = - (offer.price - offer_list[0].price) / offer.price * 100
        else:
            price_history.price_change = (offer.price - offer_list[0].price) / offer_list[0].price * 100
        return price_history.to_json(), 200
