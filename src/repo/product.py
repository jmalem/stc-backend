import os
import pandas as pd
import numpy as np
import logging
from utils import InternalError
from dotenv import load_dotenv
import gdown

# define const
load_dotenv()
PRODUCT_GDRIVE_URL = os.getenv('PRODUCT_GDRIVE_URL')

OUTPUT_DIR = "data"

# init logger
logger = logging.getLogger(__name__)


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
            df = pd.read_csv('data/data.csv', delimiter='|', on_bad_lines='skip').replace({np.nan:None})
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
