from datetime import datetime
from sqlalchemy.exc import MultipleResultsFound
from flask_misc import fl_sql


class OfferDbModel(fl_sql.Model):
    __tablename__ = 'OFFERS'

    internal_id = fl_sql.Column(fl_sql.Integer, primary_key=True)
    vendor_id = fl_sql.Column(fl_sql.Integer, nullable=False)
    price = fl_sql.Column(fl_sql.Integer, nullable=False)
    items_in_stock = fl_sql.Column(fl_sql.Integer, nullable=False)
    active = fl_sql.Column(fl_sql.Boolean, nullable=False)
    date_created = fl_sql.Column(fl_sql.DateTime, nullable=False)
    prod_id = fl_sql.Column(fl_sql.Integer, fl_sql.ForeignKey('PRODUCTS.prod_id'), nullable=False)
    product = fl_sql.relationship('ProductDbModel', overlaps='offers, PRODUCTS')

    def __init__(self, vendor_id: int, price: int, items_in_stock: int, prod_id: int):
        """
        OfferDbModel used for SQLAlchemy database
        :param vendor_id: ID of the offering vendor (type: int)
        :param price: Offered price of the product (type: int)
        :param items_in_stock: Number of products for the offered price (type: int)
        :param prod_id: ID of the offered product (type: int)
        """
        self.vendor_id = vendor_id
        self.price = price
        self.items_in_stock = items_in_stock
        self.prod_id = prod_id
        self.date_created = datetime.now()
        # assuming that newly created offer is active
        self.active = True

    def __repr__(self):
        return f'Offer internal_id = {self.internal_id}, vendor_id = {self.vendor_id}, price = {self.price}, items_in_stock = {self.items_in_stock}, active = {self.active}, date_created = {self.date_created}, prod_id = {self.prod_id}'

    def insert(self) -> "(int, OfferDbModel)":
        fl_sql.session.add(self)
        fl_sql.session.commit()
        print(self.__repr__() + ' added successfully')
        return 200, self

    @classmethod
    def find_by_vendor_id(cls, vendor_id) -> "(int, List[OfferDbModel])":
        offers = cls.query.filter_by(vendor_id=vendor_id).all()
        print(offers)
        return 200, offers

    @classmethod
    def find_by_prod_id(cls, prod_id) -> "(int, List[OfferDbModel])":
        offers = cls.query.filter_by(prod_id=prod_id).all()
        print(offers)
        return 200, offers

    @classmethod
    def find_by_prod_and_vendor_id(cls, prod_id, vendor_id) -> "(int, List[OfferDbModel])":
        offers = cls.query.filter_by(prod_id=prod_id, vendor_id=vendor_id).all()
        print(offers)
        return 200, offers

    # only one active offer at a time for specific vendor and product
    @classmethod
    def find_by_prod_and_vendor_id_active(cls, prod_id, vendor_id) -> "(int, OfferDbModel)":
        try:
            offer = cls.query.filter_by(prod_id=prod_id, vendor_id=vendor_id, active=True).one_or_none()
            if offer is None:
                status_code = 404
                print(f'No active offer for product ID = {prod_id} by vendor ID = {vendor_id} found')
            else:
                status_code = 200
                print(offer.__repr__() + ' found.')
        except MultipleResultsFound as e:
            print(e)
            offer = None
            status_code = 500
        return status_code, offer

    @classmethod
    def find_all_active(cls) -> "(int, List[OfferDbModel])":
        offers = cls.query.filter_by(active=True).all()
        print(offers)
        return 200, offers

    @classmethod
    def find_all(cls) -> "(int, List[OfferDbModel])":
        offers = cls.query.all()
        print(offers)
        return 200, offers

    @classmethod
    def delete_all(cls) -> "(int, str)":
        cls.query.all().delete(synchronize_session=False)
        fl_sql.session.commit()
        message = 'Offer history deleted'
        print(message)
        return 200, message
