import pandas as pd
import numpy as np
import logging
from utils import InternalError
logger = logging.getLogger(__name__)

TABLE_NAME = "Swatch3X"


class Product:
    def __init__(self):
        self.table = None

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

