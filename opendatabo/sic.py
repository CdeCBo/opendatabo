import datetime
import io
import warnings
from abc import ABCMeta, abstractmethod
from enum import Enum, unique
from itertools import islice
from typing import Generator, Optional

import pandas as pd
import requests
import traceback


@unique
class City(Enum):
    SANTA_CRUZ = 'sc'
    CAMIRI = 'cam'
    COCHABAMBA = 'cbba'
    TRINIDAD = 'trd'

    def to_url_part(self) -> str:
        return self.value

    @classmethod
    def all(cls):
        for city in cls:
            yield City(city.value)


class Timeframe(metaclass=ABCMeta):
    @abstractmethod
    def to_url_part(self) -> str:
        pass

    @abstractmethod
    def to_filename_suffix(self) -> str:
        pass


class Today(Timeframe):
    def to_url_part(self) -> str:
        return 'hoy'

    def to_filename_suffix(self) -> str:
        return datetime.datetime.today().strftime('%Y%m%d')


class Year(Timeframe):
    MIN_VALUE = 2008
    MAX_VALUE = datetime.datetime.now().year

    def __init__(self, value: int):
        if value < Year.MIN_VALUE or value > Year.MAX_VALUE:
            raise ValueError('value')

        self._value = value

    def to_url_part(self) -> str:
        return '{}_ano'.format(self._value)

    def to_filename_suffix(self) -> str:
        return '{}'.format(self._value)

    def __repr__(self):
        return 'Year({})'.format(self._value)

    @staticmethod
    def all_valid():
        for y in range(Year.MIN_VALUE, Year.MAX_VALUE):
            yield Year(y)


class DataNotAvailableException(Exception):
    pass


def make_market_prices_url(city: City, timeframe: Timeframe) -> str:
    return 'http://www.sicsantacruz.com/sic/sic2014/pref_{}_{}_export.php'.format(city.to_url_part(),
                                                                                  timeframe.to_url_part())


#TODO: Remove unstructured columns after cleaning them up
def prepare_raw_market_prices(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.rename(columns={'Precio Mayorista': 'precio_mayorista',
                                'Precio Minorista': 'precio_minorista',
                                'Nom_Procedencia': 'procedencia',
                                'Procedencia': 'procedencia',
                                'Mercado': 'mercado',
                                })

    # Parse string dates with format 'DD/MM/YYYY' into datetime.date objects, and replace the column data
    df.loc[:, 'fecha'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y').dt.date

    # Define the multi-index, making sure there are no index-duplicates with different data
    index_cols = ['fecha', 'producto', 'variedad']

    if df.duplicated(subset=index_cols).sum() > 0:
        warnings.warn('duplicates were found when building the dataset index. duplicates were DROPPED')
        df.drop_duplicates(subset=index_cols, keep='last', inplace=True)

    df.set_index(index_cols, inplace=True, verify_integrity=True)

    # Parse values and units
    val, unit_val, unit_name = parse_column_units(df['precio_mayorista'])
    df.loc[:, 'precio_mayorista_val'] = val
    df.loc[:, 'precio_mayorista_unit_val'] = unit_val
    df.loc[:, 'precio_mayorista_unit_name'] = unit_name

    val, unit_val, unit_name = parse_column_units(df['precio_minorista'])
    df.loc[:, 'precio_minorista_val'] = val
    df.loc[:, 'precio_minorista_unit_val'] = unit_val
    df.loc[:, 'preio_minorista_unit_name'] = unit_name

    return df


def parse_column_units(s: pd.Series) -> (pd.Series, pd.Series, pd.Series):
    parsed = s.str.extract(r'^(?P<value>\d+)\s*Bs.-/(?P<unit_raw>.*)$', expand=True)

    vals = pd.to_numeric(parsed['value'])
    units = parsed['unit_raw'].map(parse_unit, na_action='ignore')

    return vals, units.map(lambda u: u[0]), units.map(lambda u: u[1])


def parse_unit(s: str) -> (int, str):
    pound = lambda x: (x, 'lb')
    arroba = lambda x: pound(25 * x)

    static = {'Kilo':           (1,     'kg'),
              'Arroba (@)':     arroba(1),
              'Amarro':         (1,     '<amarro>'),
              'Canasta':        (1,     '<canasta>'),
              'Caja de 150U.':  (150,   'unit'),
              '100 U.':         (100,   'unit'),
              'Bolsa (2@)':     arroba(2),
              'Bolsa Grande':   (1,     '<bolsa grande>'),
              '25 U.':          (25,    'unit'),
              'Docena':         (12,    'unit'),
              'qq':             (112,   'lb'),
              'Caja de 18 Kg':  (18,    'kg'),
              'Bolsa (10@)':    arroba(10),
              'Caja de 23 Kg':  (23,    'kg'),
              'Unidad':         (1,     'unit'),
              'Libra':          (1,     'lb'),
              'Bolsa (8@)':     arroba(8),
              'Bolsa (4@)':     arroba(4),
              '3 Libras':       (3,     'lb'),
              }

    try:
        return static[s]
    except KeyError:
        raise ValueError('unknown unit: {!r}'.format(s))


def get_market_prices(city: City, timeframe: Timeframe, fformat: str = 'csv', limit: Optional[int] = None, raw: bool = False) -> pd.DataFrame:
    url = make_market_prices_url(city, timeframe)

    r = requests.post(url, data={'type': fformat, 'records': 'all'}, stream=limit is not None, allow_redirects=False)

    if r.status_code != 200:
        raise DataNotAvailableException()

    if limit is None:
        data = r.content.decode('utf-8')
    else:
        data = '\n'.join(b.decode('utf-8') for b in islice(r.iter_lines(), 0, 1 + limit))

    raw_df = pd.read_csv(io.StringIO(data))

    if raw:
        return raw_df
    else:
        return prepare_raw_market_prices(raw_df)


def save_market_prices(city: City, timeframe: Timeframe, fformat: str, raw: bool = True, output: Optional[str] = None) -> None:
    df = get_market_prices(city, timeframe, raw=raw)
    if output is None:
        output_file = 'precios_' + city.value + '_' + timeframe.to_filename_suffix() + '.' + fformat
    else:
        output_file = output
    df.to_csv(output_file)

