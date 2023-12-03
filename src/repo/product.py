import os
import pandas as pd
import numpy as np
import logging
from utils import InternalError, NotFoundError
from dotenv import load_dotenv
import re
from enum import Enum
import urllib
from cachetools import TTLCache
import json
import base64

# define const
load_dotenv()
CLOUDFRONT_BASE_URL = os.getenv('AWS_CDN_URL')
CLOUDFRONT_BACKUP_BASE_URL = os.getenv('AWS_BACKUP_CDN_URL')
IMAGE_JPG = '.jpg'
IMAGE_JPG_1 = '.JPG'
IMAGE_JPEG = '.jpeg'
IMAGE_JPEG_1 = '.JPEG'
ALTERNATE_EXT = [IMAGE_JPG_1, IMAGE_JPEG, IMAGE_JPEG_1]

S3_BUCKET_NAME = 'stc-repo-prod'
S3_IMAGE_BUCKET_NAME = 'stc-images-prod'
S3_KEY = 'HS-toys.mdb'
OUTPUT_PATH = 'data/HS-toys.mdb'

# init logger
logger = logging.getLogger(__name__)

COL_LIST = ["NAMA_BRG", "ITEM_BRG", "PACKING",
            "HARGA", "PARTAI", "Swatch_PRINT"]

SEARCH = 'search'
CATEGORY = 'category'
SORT_BY = 'sortBy'

FILE_LIST = ['data/data1.csv', 'data/data2.csv', 'data/data3.csv']


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
    def __init__(self, s3):
        self.table = None
        self.s3 = s3
        self.df = None  # data frame for swatch 1,2,3
        self.df_user = None  # data frame only for swatch 1
        self.img_cache = TTLCache(maxsize=100, ttl=1800)

    def init(self):
        """
        Pull HS-toys.mdb from stc-repo-test bucket
        """
        os.system('make clear.data')
        self.s3.meta.client.download_file(S3_BUCKET_NAME, S3_KEY, OUTPUT_PATH)

    def export_to_csv(self):
        os.system('make data')

    def load_csv(self):
        file_exists = os.path.exists('data/data1.csv') and \
                      os.path.exists('data/data2.csv') and \
                      os.path.exists('data/data3.csv')
        if file_exists:
            # init the list of csv
            li = []
            for filename in FILE_LIST:
                frame = pd.read_csv(filename, delimiter='|', on_bad_lines='skip', usecols=COL_LIST). \
                    replace({np.nan: None})
                li.append(frame)

            df = pd.concat(li, axis=0, ignore_index=True)

            df = dataframe_aggregation(df)
            self.df = df

            # initialize data fram for USER and GUEST (contains swatch 1)
            df_user = dataframe_aggregation(li[0])
            self.df_user = df_user
        else:
            raise InternalError('data not found')

    def list(self, filters, role):
        try:
            df = self.df
            if role == 'GUEST' or role == 'USER':
                df = self.df_user
            # apply filter
            if type(filters) is not dict:
                raise InternalError('Filter type error')
            chain = None
            search = filters.get(SEARCH)
            if search:
                keywords = search.split(' ')
                base = r'{}'
                expr = '(?=.*{})'
                search_reg = base.format(''.join(expr.format(w) for w in keywords))
                chain = (df['displayId'].str.contains(search, na=False, case=False)
                         | df['title'].str.contains(search_reg, na=False, case=False))

            category = filters.get(CATEGORY)
            if category:
                if chain is None:
                    chain = df['category'].isin([category])
                else:
                    chain = chain & df['category'].isin([category])

            if chain is not None:
                df = df.loc[chain]

            sort_by = filters.get(SORT_BY)
            if sort_by:
                sort_key = "unitPrice" if sort_by == SortBy.PRICE_ASC.name or sort_by == SortBy.PRICE_DESC.name else "title"
                is_asc = sort_by == SortBy.PRICE_ASC.name or sort_by == SortBy.NAME_ASC.name
                df = df.sort_values(by=sort_key, ascending=is_asc)
            else:
                # By default sort in ascending order of Item ID
                df = df.sort_values(by="itemId")

            if role == 'GUEST':
                # have to create shallow copy here, as dropping the column directly
                # will also alter the original dataframe
                new_df = df.drop(['unitPrice'], axis=1)
                return new_df.to_dict(orient="records")

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

    def get(self, item_id, role):
        try:
            df = self.df.loc[self.df['itemId'] == item_id].head(1)
            if role == 'GUEST' or role == 'USER':
                df = self.df_user.loc[self.df['itemId'] == item_id].head(1)
            if len(df.index) == 0:
                raise NotFoundError('item not found')

            # df is a copy of the single item from the original dataframe
            if role == 'GUEST':
                df.drop(['unitPrice'], axis=1, inplace=True)
            medias = self.img_cache.get(item_id, [])
            if len(medias) == 0:
                print('no cache found for ', item_id, ', add cache')
                objs = self.s3.meta.client.list_objects_v2(
                    Bucket=S3_IMAGE_BUCKET_NAME,
                    Prefix=item_id,
                    EncodingType='url',
                    MaxKeys=5
                )

                contents = objs.get('Contents', [])
                for c in contents:
                    key = c.get('Key')
                    url = CLOUDFRONT_BASE_URL + key
                    if ".mp4" in key:
                        url = CLOUDFRONT_BACKUP_BASE_URL + key
                    medias.append(url)
                self.img_cache[item_id] = medias
            else:
                print('cache found for ', item_id)

            tmp = df.to_dict(orient="records")
            # to_dict returns an array hence the [0]
            # and we are doing it here since panda cannot handle multiple value in 1 cell
            # we have to concat it into a string and split it again
            # Hence it will be more performant to append it here
            tmp[0]['mediaObjs'] = medias
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


# change the data frame, columns, and apply filters
def dataframe_aggregation(df):
    df.rename(columns={
        'ITEM_BRG': 'displayId',
        'NAMA_BRG': 'title',
        'Swatch_PRINT': 'itemId',
        'PARTAI': 'category',
    }, inplace=True)
    # Extract price out of HARGA
    df['unitPrice'] = df.apply(lambda x: getPrice(x['HARGA']), axis=1)

    # Generates imageUrl in cloudfront (not always available)
    df['imageUrl'] = df.apply(create_encoded_url, axis=1)
    df['alternateImageUrls'] = df.apply(create_alternate_encoded_url, axis=1)
    # df['imageUrl'] = df.apply(
    #     lambda x: CLOUDFRONT_BASE_URL + urllib.parse.quote(str(x['itemId'])) + IMAGE_JPG, axis=1) # TODO: comment out this one

    # Extract packing and unit from PACKING
    df[['packing', 'unit']] = df.apply(lambda x: pd.Series(
        extract_packing_and_unit(str(x['PACKING']))), axis=1)

    # drop unwanted column
    df.drop(['HARGA', 'PACKING'], axis=1, inplace=True)
    return df


# create base64 encoded url to access image through serverless image handler
def create_encoded_url(item):
    item_key = str(item['itemId']) + IMAGE_JPG
    item_json = {
        "bucket": S3_IMAGE_BUCKET_NAME,
        "key": item_key,
        "edits": {
            "resize": {
                "width": 400,
                "fit": "contain"
            }
        }
    }
    jsonStr = json.dumps(item_json)
    return CLOUDFRONT_BASE_URL + base64.b64encode(jsonStr.encode()).decode()


def create_alternate_encoded_url(item):
    res = []
    for ext in ALTERNATE_EXT:
        item_key = str(item['itemId']) + ext
        item_json = {
            "bucket": S3_IMAGE_BUCKET_NAME,
            "key": item_key,
            "edits": {
                "resize": {
                    "width": 400,
                    "fit": "contain"
                }
            }
        }
        jsonStr = json.dumps(item_json)
        res.append(CLOUDFRONT_BASE_URL + base64.b64encode(jsonStr.encode()).decode())
    return res

# How the url works in FE
# 1. try the imageUrl
# 2. if imageUrl fail, craft a new json (pake itemId) with .JPG/.JPEG/.jpeg and then encode it
# 3. use that in place of the old imageUrl
