from datetime import datetime
from operator import and_

from sqlalchemy.exc import IntegrityError
from typing import List

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

        :param vendor_id: ID of the offering vendor (int)
        :param price: Offered price of the product (int)
        :param items_in_stock: Number of products for the offered price (int)
        :param prod_id: ID of the offered product (int)
        """
        self.vendor_id = vendor_id
        self.price = price
        self.items_in_stock = items_in_stock
        self.prod_id = prod_id
        self.date_created = datetime.now()
        # assuming that newly created offer is active
        self.active = True

    def __repr__(self):
        """
        Return string representation of the OfferDbModel

        :return: - 'str' representing offer
        """
        return f'Offer internal_id = {self.internal_id}, vendor_id = {self.vendor_id}, price = {self.price}' \
               f', items_in_stock = {self.items_in_stock}, active = {self.active}, date_created = {self.date_created}' \
               f', prod_id = {self.prod_id}'

    def insert(self) -> "bool":
        """
        Insert offer into DB

        :return: - 'bool' representing success of the operation
        """
        query_data = self.find_by_prod_and_vendor_id_active(prod_id=self.prod_id, vendor_id=self.vendor_id)
        if query_data is not None:
            # unless it has the same price and items in stock -> we don't need duplicates
            if query_data.price != self.price or \
                    query_data.items_in_stock != self.items_in_stock:
                setattr(query_data, 'active', False)
            else:
                return False
        try:
            fl_sql.session.add(self)
            fl_sql.session.commit()
            return True
        except IntegrityError:
            fl_sql.session.rollback()
            return False

    @classmethod
    def find_by_vendor_id(cls, vendor_id) -> "List[OfferDbModel]":
        """
        Find all offers by vendor ID

        :param vendor_id: Offers' vendor ID (int)
        :returns: - 'List[OfferDbModel] representing all offers
        """
        return cls.query.filter_by(vendor_id=vendor_id).all()

    @classmethod
    def find_by_prod_id(cls, prod_id) -> "List[OfferDbModel]":
        """
        Find all offers by product ID

        :param prod_id: Offers' product ID (int)
        :returns: - 'List[OfferDbModel] representing all offers
        """
        return cls.query.filter_by(prod_id=prod_id).all()

    @classmethod
    def find_by_prod_and_vendor_id(cls, prod_id, vendor_id) -> "List[OfferDbModel]":
        """
        Find all offers by vendor ID and product ID

        :param prod_id: Offers' product ID (int)
        :param vendor_id: Offers' vendor ID (int)
        :returns: - 'List[OfferDbModel] representing all offers
        """
        return cls.query.filter_by(prod_id=prod_id, vendor_id=vendor_id).all()

    @classmethod
    def find_by_prod_and_vendor_id_active(cls, prod_id, vendor_id) -> "OfferDbModel":
        """
        Find all active offers by vendor ID and product ID

        :param prod_id: Offers' product ID (int)
        :param vendor_id: Offers' vendor ID (int)
        :returns: - 'List[OfferDbModel] representing all active offers
        """
        return cls.query.filter_by(prod_id=prod_id, vendor_id=vendor_id, active=True).one_or_none()

    @classmethod
    def find_all_active(cls) -> "List[OfferDbModel]":
        """
        Find all active offers

        :returns: - 'List[OfferDbModel] representing all active offers
        """
        return cls.query.filter_by(active=True).all()

    @classmethod
    def find_all(cls) -> "List[OfferDbModel]":
        """
        Find all offers

        :returns: - 'List[OfferDbModel] representing all offers
        """
        return cls.query.all()

    @classmethod
    def find_by_prod_id_and_vendor_id_between_dates(cls, prod_id: int, vendor_id: int, date_start: str,
                                                    date_end: str) -> "List[OfferDbModel]":
        """
        Find all offers by vendor ID and product ID between two dates

        :param prod_id: Offers' product ID (int)
        :param vendor_id: Offers' vendor ID (int)
        :param date_start: Starting date of search
        :param date_end: Ending date of search
        :returns: - 'List[OfferDbModel] representing all offers
        """
        from_date = datetime.strptime(date_start, '%Y-%m-%dT%H:%M:%S.%f')
        to_date = datetime.strptime(date_end, '%Y-%m-%dT%H:%M:%S.%f')
        return cls.query.filter_by(prod_id=prod_id, vendor_id=vendor_id).filter(
            and_(cls.date_created >= from_date, cls.date_created <= to_date)).order_by(cls.date_created.asc()).all()

    # @classmethod
    # def delete_all(cls) -> "(int, str)":
    #     cls.query.all().delete(synchronize_session=False)
    #     fl_sql.session.commit()
    #     message = 'Offer history deleted'
    #     print('Offer history deleted')
    #     return 200, message
