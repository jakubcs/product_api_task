from sqlalchemy.exc import IntegrityError
from typing import List
from flask_misc import fl_sql

NAME_MAX_LENGTH = 100
DESCRIPTION_MAX_LENGTH = 200


class ProductDbModel(fl_sql.Model):
    __tablename__ = 'PRODUCTS'

    prod_id = fl_sql.Column(fl_sql.Integer, primary_key=True)
    # We don't want to have multiple DB items with the same name
    name = fl_sql.Column(fl_sql.String(NAME_MAX_LENGTH), nullable=False, unique=True)
    description = fl_sql.Column(fl_sql.String(DESCRIPTION_MAX_LENGTH), nullable=False)

    offers = fl_sql.relationship('OfferDbModel', lazy='dynamic',
                                 primaryjoin='ProductDbModel.prod_id == OfferDbModel.prod_id', backref='PRODUCTS',
                                 overlaps='product, PRODUCTS')

    def __init__(self, name: str, description: str):
        """
        ProductDbModel used for SQLAlchemy database

        :param name: Name of the product (str)
        :param description: Description of the product (str)
        """
        name = name.strip()
        if len(name) <= 0 or len(name) > NAME_MAX_LENGTH:
            raise ValueError(f'Parameter name should have between 1 and {NAME_MAX_LENGTH} characters, '
                             f'but it has {len(name)} characters.')

        description = description.strip()
        if len(description) <= 0 or len(description) > DESCRIPTION_MAX_LENGTH:
            raise ValueError(f'Parameter description should have between 1 and {DESCRIPTION_MAX_LENGTH} characters, '
                             f'but it has {len(description)} characters.')

        self.name = name
        self.description = description

    def __repr__(self):
        """
        Return string representation of the ProductDbModel

        :returns: - 'str' representing product
        """
        return f'Product prod_id = {self.prod_id}, name = "{self.name}", description = "{self.description}"'

    def insert(self) -> "bool":
        """
        Insert product into DB

        :return: - 'bool' representing success of the operation
        """
        try:
            fl_sql.session.add(self)
            fl_sql.session.commit()
        except IntegrityError:
            fl_sql.session.rollback()
            return False
        return True

    def update(self, data) -> "bool":
        """
        Insert product into DB.

        :param data: json string containing data and values to be updated (str)
        :return: - 'bool' representing success of the operation
        """
        try:
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            fl_sql.session.commit()
        except IntegrityError:
            fl_sql.session.rollback()
            return False
        return True

    @classmethod
    def find_by_id(cls, prod_id: int) -> "ProductDbModel":
        """
        Find product by product ID

        :param prod_id: Product ID (int)
        :returns: - 'ProductDbModel' representing product
        """
        # We assume that the product ID is unique in used DB; if not, there is something wrong
        return cls.query.filter_by(prod_id=prod_id).one_or_none()

    # TODO refactor with above?
    @classmethod
    def find_by_name_exact(cls, name: str) -> "ProductDbModel":
        """
        Find product by product name

        :param name: Product name (str)
        :returns: - 'ProductDbModel' representing product
        """
        # We assume that the product name is unique in used DB; if not, there is something wrong
        return cls.query.filter_by(name=name).one_or_none()

    @classmethod
    def find_all(cls) -> "List[ProductDbModel]":
        """
        Find all products

        :returns: - 'List[ProductDbModel] representing all products
        """
        return cls.query.all()

    @classmethod
    def delete_by_id(cls, prod_id: int) -> "bool":
        """
        Delete product by product ID

        :param prod_id: Product ID (int)
        :returns: - 'bool' representing success of the operation
        """
        deleted = cls.query.filter_by(prod_id=prod_id).delete(synchronize_session='fetch')
        if deleted:
            fl_sql.session.commit()
            return True
        return False
