import json

from flask import request
from flask_restx import Resource, fields, Namespace
from offer_db_model import OfferDbModel
from offer_db_schema import OfferDbSchema

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


class OfferList(Resource):
    @staticmethod
    @offers_ns.doc('Get all offers')
    @offers_ns.response(200, 'Ok', [offer_model_res])
    def get() -> "(str, int)":
        """
        Get list of all offers
        """
        status_code, offer_list = OfferDbModel.find_all()
        return offer_list_schema.dump(offer_list), status_code


class ActiveOfferList(Resource):
    @staticmethod
    @offers_ns.doc('Get all active offers')
    @offers_ns.response(200, 'Ok', [offer_model_res])
    def get() -> "(str, int)":
        """
        Get list of all active offers
        """
        status_code, offer_list = OfferDbModel.find_all_active()
        return offer_list_schema.dump(offer_list), status_code


class VendorOfferList(Resource):
    @staticmethod
    @offers_ns.doc('Get all offers by vendor ID')
    @offers_ns.response(200, 'Ok', [offer_model_res])
    def get(vendor_id: int) -> "(str, int)":
        """
        Get list of all offers for given vendor ID
        """
        status_code, offer_list = OfferDbModel.find_by_vendor_id(vendor_id)
        return offer_list_schema.dump(offer_list), status_code


class ProductOfferList(Resource):
    @staticmethod
    @offers_ns.doc('Get all offers by product ID')
    @offers_ns.response(200, 'Ok', [offer_model_res])
    @offers_ns.response(404, 'Not found', str)
    def get(prod_id: int) -> "(str, int)":
        """
        Get list of all offers for given product ID
        """
        status_code, offer_list = OfferDbModel.find_by_prod_id(prod_id)
        return offer_list_schema.dump(offer_list), status_code


class PriceHistoryItem:
    def __init__(self, price: int, date_created: str):
        self.price = price
        self.date_created = date_created

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


class PriceHistory:
    def __init__(self, prod_id: int, vendor_id: int, history: [PriceHistoryItem]):
        self.prod_id = prod_id
        self.vendor_id = vendor_id
        self.history = history
        self.price_change = 0

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


class ProductAndVendorOfferHistoryList(Resource):
    @staticmethod
    @offers_ns.expect(date_interval_item)
    @offers_ns.doc('Get the price history of a product for specific vendor')
    @offers_ns.response(200, 'Ok', price_history_model)
    def post(prod_id: int, vendor_id: int) -> "(str, int)":
        """
        Get price history of a specific product offered by a specific vendor
        """
        date_interval_json = request.get_json()
        date_start = date_interval_json['date_start']
        date_end = date_interval_json['date_end']
        status_code, offer_list = OfferDbModel.find_by_prod_id_and_vendor_id_between_dates(prod_id, vendor_id,
                                                                                           date_start, date_end)
        if len(offer_list) == 0:
            price_history = PriceHistory(prod_id=prod_id, vendor_id=vendor_id, history=[])
            return price_history.to_json(), 200

        price_history_data = []
        for offer in offer_list:
            price_history_data.append(PriceHistoryItem(price=offer.price, date_created=str(offer.date_created)))
        price_history = PriceHistory(prod_id=prod_id, vendor_id=vendor_id, history=price_history_data)
        price_history.price_change = (offer.price - offer_list[0].price) / offer.price * 100
        return price_history.to_json(), status_code
