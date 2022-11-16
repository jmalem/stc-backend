import pprint
import boto3
import os
from flask import Flask
from flask_restful import Api
from src.service import Signup, Login, Product, ProductBuild, ProductDetail, Order as OrderSvc, Ping, Customer, \
    CustomerBuild
from dotenv import load_dotenv
from src.repo.user import User
from src.repo.order import Order
from src.repo.product import Product as ProductRepo
from src.repo.customer import Customer as CustomerRepo
from flask_cors import CORS

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_TABLE_REGION = os.getenv('AWS_TABLE_REGION')

USER_DB_NAME = "stc-user"
ORDER_DB_NAME = "stc-order"

# TODO: create .env file with your credentials
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_TABLE_REGION
)
dynamodb_client = boto3.client(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_TABLE_REGION
)

# Alternative
# session = boto3.Session(profile_name='<your-aws-config-profile-name-here>')
# dynamodb_client = session.client('dynamodb')

app = Flask(__name__)
CORS(app)
api = Api(app)


def init_repo():
    # Check if table exists
    dynamodb = session.resource('dynamodb')
    user_db = User(dynamodb)
    user_db_exists = user_db.exists(USER_DB_NAME)
    if not user_db_exists:
        print(f"\nCreating table {USER_DB_NAME}...")
        user_db.create_table(USER_DB_NAME)
        print(f"\nCreated table {user_db.table.name}.")

    order_db = Order(dynamodb)
    order_db_exists = order_db.exists(ORDER_DB_NAME)
    if not order_db_exists:
        print(f"\nCreating table {ORDER_DB_NAME}...")
        order_db.create_table(ORDER_DB_NAME)
        print(f"\nCreated table {order_db.table.name}.")

    print(order_db.list_tables())

    # Init s3 session, and pass it to product repo
    s3 = session.resource('s3')
    product_db = ProductRepo(s3)

    #
    customer_db = CustomerRepo(s3)

    # Debugging DB instantiation - check region, capacity, etc
    # response = dynamodb_client.describe_table(TableName=USER_DB_NAME)
    # pprint.pprint(response)

    # Will download mdb and build product
    try:
        file_exists = os.path.exists('data/data.csv')
        if not file_exists:
            print("trying to download new mdb file..")
            product_db.init()
            print("converts mdb to csv file..")
            product_db.export_to_csv()
        cust_file_exists = os.path.exists('data/customer.xlsx')
        if not cust_file_exists:
            print("trying to download new xlsx file..")
            customer_db.init()
        print("loading csv file..")
        product_db.load_csv()
        print("loading customer file..")
        customer_db.load_customer()
        print("data loads successful")
    except Exception as e:
        print("warn: csv is corrupt or doesnt exist, will need to re-init product list", e)
        pass

    api.add_resource(Ping, '/ping')
    api.add_resource(Signup, '/signup', resource_class_kwargs={'repo': user_db})
    api.add_resource(Login, '/login', resource_class_kwargs={'repo': user_db})
    api.add_resource(Product, '/product', resource_class_kwargs={'repo': product_db, 'user_repo': user_db})
    api.add_resource(ProductDetail, '/product/<item_id>',
                     resource_class_kwargs={'repo': product_db, 'user_repo': user_db})
    api.add_resource(ProductBuild, '/product:build', resource_class_kwargs={'repo': product_db, 'user_repo': user_db})
    api.add_resource(OrderSvc, '/order', resource_class_kwargs={'repo': order_db, 'user_repo': user_db})
    api.add_resource(Customer, '/customer', resource_class_kwargs={'repo': customer_db, 'user_repo': user_db})
    api.add_resource(CustomerBuild, '/customer:build', resource_class_kwargs={'repo': customer_db, 'user_repo': user_db})


if __name__ == '__main__':
    init_repo()
    port = os.getenv('PORT', default=5000)
    app.run(debug=True, host='0.0.0.0', port=port)
