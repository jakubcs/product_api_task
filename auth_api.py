from flask_restx import Resource, fields, Namespace

auth_ns = Namespace('auth', description='Authentication related operations')

token_body = {'access_token': fields.String('Access token for API')}

token_model = auth_ns.model(name='Token', model=token_body)

# can be replaced with some UUID or something else
secret_token = 'very_secret_key'


def evaluate_token(token: str) -> "(str, int)":
    if token is None:
        return 'Unauthorized request', 401
    elif token != secret_token:
        return 'Forbidden access', 403
    else:
        return 'Ok', 200


class RequestToken(Resource):
    @staticmethod
    @auth_ns.doc('Request authentication token')
    @auth_ns.response(201, 'Ok', token_model)
    def post():
        """
        Request authentication token
        """
        return {'access_token': 'very_secret_key'}, 201
