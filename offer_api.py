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

offer_model_res = offers_ns.model(name='Offer', model=offer_body_res)


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
    def get(prod_id: int) -> "(str, int)":
        """
        Get list of all offers for given product ID
        """
        status_code, offer_list = OfferDbModel.find_by_prod_id(prod_id)
        return offer_list_schema.dump(offer_list), status_code
