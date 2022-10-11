import os
import pandas as pd
import numpy as np
import logging
from utils import InternalError
from dotenv import load_dotenv
import gdown
import re

# define const
load_dotenv()
PRODUCT_GDRIVE_URL = os.getenv('PRODUCT_GDRIVE_URL')
CLOUDFRONT_BASE_URL = 'd2x2qav5m49n4.cloudfront.net/'
IMAGE_JPG = '.jpg'
OUTPUT_DIR = "data"

# init logger
logger = logging.getLogger(__name__)

COL_LIST = ["NAMA_BRG", "ITEM_BRG", "PACKING", "HARGA", "PARTAI", "Swatch_PRINT"]


def extract_packing_and_unit(dt):
    packing = dt.split(" ")
    return packing[0], packing[-1]


class Product:
    def __init__(self):
        self.table = None

    def init(self):
        """
        Pull the specific GDrive directory that contains HS-toys.mdb

        The reason why we download the folder
        Setting permissions on folders are much easier than changing perms for individual files

        with individual files, FE need to always pass the url/file id for the new uploaded .mdb file
        """
        url = PRODUCT_GDRIVE_URL
        gdown.download_folder(url=url, output=OUTPUT_DIR, quiet=False, use_cookies=False)

    def export_to_csv(self):
        os.system('make data')

    def list(self):
        try:
            df = pd.read_csv('data/data.csv', delimiter='|', on_bad_lines='skip', usecols=COL_LIST). \
                replace({np.nan: None})

            df.rename(columns={
                'ITEM_BRG': 'displayId',
                'NAMA_BRG': 'title',
                'Swatch_PRINT': 'itemId',
                'PARTAI': 'category',
            }, inplace=True)
            # Extract price out of HARGA
            df['unitPrice'] = df.apply(lambda x: re.sub("[^0-9]", "", str(x['HARGA'])), axis=1)

            # Generates imageUrl in cloudfront (not always available)
            df['imageUrl'] = df.apply(lambda x: CLOUDFRONT_BASE_URL + str(x['itemId']) + IMAGE_JPG, axis=1)

            # Extract packing and unit from PACKING
            df[['packing', 'unit']] = df.apply(lambda x: pd.Series(extract_packing_and_unit(str(x['PACKING']))), axis=1)

            # drop unwanted column
            df.drop(['HARGA', 'PACKING'], axis=1, inplace=True)
            tmp = df.to_dict(orient="records")
            return tmp
        except FileNotFoundError:
            raise InternalError('Product list cannot be built')
        except pd.errors.EmptyDataError as e:
            raise InternalError('Product list empty')
        except pd.errors.ParserError as e:
            raise InternalError('Product list cannot be parsed')
        except Exception as e:
            raise InternalError('Failed to list', e)

