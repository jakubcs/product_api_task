# product_api_task

Before start, make sure that you have defined OFFER_BASE_URL environmental variable equal to the base URL of the
external offers' microservice. Optionally, you can define OFFER_AUTH_CODE environmental variable if you don't have a
token to access this microservice. If this environmental variable is not set, the application will automatically request
a new token from the offers' microservice (note: to export variables while creating docker container, you can use .env
file with VAR_NAME=VAR_VALUE rows).

Upon starting the app, API documentation can be found at base_url/api/doc. Except for /auth POST request, every request
must be accompanied by header containing bearer token; e.g., assuming base_url=http://localhost:5000 and windows command
line environment, one can send request using a curl command as follows:

curl -H "Content-Type: application/json" -H "Bearer: insert_token" -X POST http://localhost:5000/api/products -d "
{\"name\": \"apple\", \"description\": \"apple\"}"

This particular request can be used to add a new product to product database. Please note that the application creates
databases just before receiving a first request.

In 'tests' folder, there is also a file called 'test_basic.py' that defines several simple scenarios to test basic
functionality.