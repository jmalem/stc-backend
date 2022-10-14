import os
import pandas as pd
import numpy as np
import logging
from utils import InternalError, NotFoundError
from dotenv import load_dotenv
import gdown
import re
from enum import Enum

# define const
load_dotenv()
PRODUCT_GDRIVE_URL = os.getenv('PRODUCT_GDRIVE_URL')
CLOUDFRONT_BASE_URL = 'd2x2qav5m49n4.cloudfront.net/'
IMAGE_JPG = '.jpg'
OUTPUT_DIR = "data"

# init logger
logger = logging.getLogger(__name__)

COL_LIST = ["NAMA_BRG", "ITEM_BRG", "PACKING", "HARGA", "PARTAI", "Swatch_PRINT"]

SEARCH = 'search'
CATEGORY = 'category'
SORT_BY = 'sortBy'


def extract_packing_and_unit(dt):
    packing = dt.split(" ")
    return packing[0], packing[-1]


class SortBy(Enum):
    NONE = 0
    PRICE_ASC = 1
    PRICE_DESC = 2
    NAME_ASC = 3
    NAME_DESC = 4


def getPrice(price):
    new_price = re.sub("[^0-9]", "", str(price))
    if new_price != "":
        return int(new_price)
    return 0


class Product:
    def __init__(self):
        self.table = None

        # init the csv
        df = pd.read_csv('data/data.csv', delimiter='|', on_bad_lines='skip', usecols=COL_LIST). \
            replace({np.nan: None})

        df.rename(columns={
            'ITEM_BRG': 'displayId',
            'NAMA_BRG': 'title',
            'Swatch_PRINT': 'itemId',
            'PARTAI': 'category',
        }, inplace=True)
        # Extract price out of HARGA
        df['unitPrice'] = df.apply(lambda x: getPrice(x['HARGA']), axis=1)

        # Generates imageUrl in cloudfront (not always available)
        df['imageUrl'] = df.apply(lambda x: CLOUDFRONT_BASE_URL + str(x['itemId']) + IMAGE_JPG, axis=1)

        # Extract packing and unit from PACKING
        df[['packing', 'unit']] = df.apply(lambda x: pd.Series(extract_packing_and_unit(str(x['PACKING']))), axis=1)

        # drop unwanted column
        df.drop(['HARGA', 'PACKING'], axis=1, inplace=True)

        self.df = df

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

    def list(self, filters):
        try:
            df = self.df
            # apply filter
            if type(filters) is not dict:
                raise InternalError('Filter type error')
            chain = None
            search = filters.get(SEARCH)
            if search:
                chain = df['displayId'].str.contains(search, na=False)

            category = filters.get(CATEGORY)
            if category:
                chain = chain & df['category'].str.contains(category, na=False)

            if chain is not None:
                df = df.loc[chain]

            sort_by = filters.get(SORT_BY)
            if sort_by:
                sort_key = "unitPrice" if sort_by == SortBy.PRICE_ASC.name or sort_by == SortBy.PRICE_DESC.name else "title"
                is_asc = sort_by == SortBy.PRICE_ASC.name or sort_by == SortBy.NAME_ASC.name
                df = df.sort_values(by=sort_key, ascending=is_asc)

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

    def get(self, item_id):
        try:

            df = self.df.loc[self.df['itemId'] == item_id].head(1)
            if len(df.index) == 0:
                raise NotFoundError('item not found')

            tmp = df.to_dict(orient="records")
            return tmp
        except FileNotFoundError:
            raise InternalError('Product list cannot be built')
        except pd.errors.EmptyDataError as e:
            raise InternalError('Product list empty')
        except pd.errors.ParserError as e:
            raise InternalError('Product list cannot be parsed')
        except NotFoundError as e:
            raise e
        except Exception as e:
            raise InternalError('Failed to list', e)
