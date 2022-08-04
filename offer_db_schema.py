from flask_misc import fl_mar
from offer_db_model import OfferDbModel


class OfferDbSchema(fl_mar.SQLAlchemyAutoSchema):
    class Meta:
        model = OfferDbModel
        load_instance = True
        include_fk = True
