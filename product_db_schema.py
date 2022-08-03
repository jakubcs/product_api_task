from flask_misc import fl_mar
from product_db_model import ProductDbModel


class ProductDbSchema(fl_mar.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductDbModel
        load_instance = True
        include_fk = True
