import pprint
import boto3
import os
from flask import Flask
from flask_restful import Api
from src.service import Signup
from src.service import Login
from dotenv import load_dotenv
from src.repo.user import User

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_TABLE_REGION = os.getenv('AWS_TABLE_REGION')

USER_DB_NAME = "stc-user"

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

    print(user_db.list_tables())

    # Debugging DB instantiation - check region, capacity, etc
    # response = dynamodb_client.describe_table(TableName=USER_DB_NAME)
    # pprint.pprint(response)

    api.add_resource(Signup, '/signup', resource_class_kwargs={'repo': user_db})
    api.add_resource(Login, '/login', resource_class_kwargs={'repo': user_db})


if __name__ == '__main__':
    init_repo()
    app.run(debug=True)
