from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

fl_mar = Marshmallow()
fl_sql = SQLAlchemy()

RESPONSE200 = 'Ok'
RESPONSE204 = 'Resource deleted successfully'
RESPONSE400 = 'Bad request'
RESPONSE401 = 'Unauthorized access'
RESPONSE403 = 'Forbidden access'
RESPONSE500 = 'Unexpected DB error - multiple products with same product ID found'
