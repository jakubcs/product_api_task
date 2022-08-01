from flask_misc import fl_mar, fl_sql
from sqlalchemy.orm.exc import MultipleResultsFound

NAME_MAX_LENGTH = 100
DESCRIPTION_MAX_LENGTH = 200


class ProductDbModel(fl_sql.Model):
    __tablename__ = 'PRODUCTS'

    prod_id = fl_sql.Column(fl_sql.Integer, primary_key=True)
    # We don't want to have multiple DB items with the same name
    name = fl_sql.Column(fl_sql.String(NAME_MAX_LENGTH), nullable=False, unique=True)
    description = fl_sql.Column(fl_sql.String(DESCRIPTION_MAX_LENGTH), nullable=False)

    # TODO define DB relationship with offers

    def __init__(self, name: str, description: str):
        """
        ProductDbModel used for SQLAlchemy database
        :param name: Name of the product (type: str)
        :param description: Description of the product (type: str)
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
        return f'Product prod_id = {self.prod_id}, name = "{self.name}", description = "{self.description}"'

    def insert(self) -> "(int, ProductDbModel)":
        fl_sql.session.add(self)
        fl_sql.session.commit()
        print(self.__repr__() + ' added successfully.')
        return 200, self

    def update(self, data) -> "(int, ProductDbModel)":
        message = f'Product with ID = {self.prod_id} updated fields:'
        for key, value in data.items():
            setattr(self, key, value)
            message = message + f' {key} = {value},'
        message = message[:-1] + '.'
        fl_sql.session.commit()
        print(message)
        return 200, self

    @classmethod
    def find_by_id(cls, prod_id: int) -> "(int, ProductDbModel)":
        # We assume that the product ID is unique in used DB; if not, there is something wrong
        try:
            ret_model = cls.query.filter_by(prod_id=prod_id).one_or_none()
            if ret_model is None:
                status_code = 404
                print(f'Product with ID = {prod_id} not found.')
            else:
                status_code = 200
                print(ret_model.__repr__() + ' found.')
        except MultipleResultsFound as e:
            print(e)
            ret_model = None
            status_code = 500

        return status_code, ret_model

    # TODO refactor with above?
    @classmethod
    def find_by_name_exact(cls, name: str) -> "(int, ProductDbModel)":
        # We assume that the product name is unique in used DB; if not, there is something wrong
        try:
            ret_model = cls.query.filter_by(name=name).one_or_none()
            if ret_model is None:
                status_code = 404
                print(f'Product with name = {name} not found.')
            else:
                status_code = 200
                print(ret_model.__repr__() + ' found.')
        except MultipleResultsFound as e:
            print(e)
            ret_model = None
            status_code = 400

        return status_code, ret_model

    @classmethod
    def find_all(cls) -> "(int, List[ProductDbModel])":
        products = cls.query.all()
        print(products)
        return 200, products

    @classmethod
    def delete_by_id(cls, prod_id: int) -> "(int, str)":
        deleted = cls.query.filter_by(prod_id=prod_id).delete(synchronize_session=False)
        if deleted:
            fl_sql.session.commit()
            message = f'Product with ID = {prod_id} successfully deleted'
            return 200, message
        else:
            message = f'Could not delete a product with ID = {prod_id} as it is not present in the database.'
            return 404, message


class ProductDbSchema(fl_mar.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductDbModel
        load_instance = True
        include_fk = True
