import os
import pandas as pd
import logging
from utils import InternalError
from dotenv import load_dotenv

# define const
load_dotenv()
S3_CUSTOMER_BUCKET_NAME = 'stc-customer-prod'
CUSTOMER_S3_KEY = 'customer.xlsx'
CUSTOMER_OUTPUT_PATH = 'data/customer.xlsx'

# init logger
logger = logging.getLogger(__name__)
COL_LIST = ['CUST_NAME']

class Customer:
    def __init__(self, s3):
        self.s3 = s3
        self.customer = None

    def init(self):
        """
        Pull customer.xlsx from stc-customer-test bucket
        """
        self.s3.meta.client.download_file(S3_CUSTOMER_BUCKET_NAME, CUSTOMER_S3_KEY, CUSTOMER_OUTPUT_PATH)

    def load_customer(self):
        file_exists = os.path.exists('data/customer.xlsx')
        if file_exists:
            # init the csv
            df = pd.DataFrame(pd.read_excel(CUSTOMER_OUTPUT_PATH, usecols=COL_LIST))

            df.rename(columns={
                'CUST_NAME': 'customer',
            }, inplace=True)
            self.customer = df
        else:
            raise InternalError('customer data not found')

    def list(self):
        try:
            df = self.customer
            return df['customer'].tolist()
        except FileNotFoundError:
            raise InternalError('Customer list cannot be built')
        except pd.errors.EmptyDataError as e:
            raise InternalError('Customer list empty')
        except pd.errors.ParserError as e:
            raise InternalError('Customer list cannot be parsed')
        except Exception as e:
            raise InternalError('Failed to list customers', e)
