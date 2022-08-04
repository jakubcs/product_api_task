from flask_restx import Resource, fields, Namespace

auth_ns = Namespace('auth', description='Authentication related operations')
token_body = {'access_token': fields.String('Access token for API')}
token_model = auth_ns.model(name='Token', model=token_body)
# can be replaced with some UUID or something else
secret_token = 'very_secret_key'


def evaluate_token(token: str) -> "(str, int)":
    """
    Evaluate authentication token

    :param token: Authentication token to be evaluated (str)
    :returns:
        - info - 'str' containing additional info
        - sc - 'int' representing HTTP status code
    """
    if token is None:
        return 'Unauthorized request - use valid bearer token to authorize', 401
    elif token != secret_token:
        return 'Forbidden access - use valid bearer token to authorize', 403
    else:
        return 'Ok', 200


class RequestToken(Resource):
    @staticmethod
    @auth_ns.doc('Request authentication token')
    @auth_ns.response(201, 'Ok', token_model)
    def post() -> "(str, int)":
        """
        Request authentication token. Return access_token and HTTP status code

        :returns:
            - info - 'str' json containing access_token
            - sc - 'int' representing HTTP status code
        """
        return {'access_token': 'very_secret_key'}, 201
