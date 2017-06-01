import datetime
import io
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


class Today(Timeframe):
    def to_url_part(self) -> str:
        return 'hoy'


class Year(Timeframe):
    MIN_VALUE = 2008
    MAX_VALUE = datetime.datetime.now().year

    def __init__(self, value: int):
        if value < Year.MIN_VALUE or value > Year.MAX_VALUE:
            raise ValueError('value')

        self._value = value

    def to_url_part(self) -> str:
        return '{}_ano'.format(self._value)

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


def prepare_raw_market_prices(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.rename(columns={'Precio Mayorista': 'precio_mayorista',
                                'Precio Minorista': 'precio_minorista',
                                'Nom_Procedencia': 'procedencia',
                                'Procedencia': 'procedencia',
                                })

    return df


def get_market_prices(city: City, timeframe: Timeframe, limit: Optional[int] = None) -> pd.DataFrame:
    url = make_market_prices_url(city, timeframe)

    r = requests.post(url, data={'type': 'csv', 'records': 'all'}, stream=True, allow_redirects=False)

    if r.status_code != 200:
        raise DataNotAvailableException()

    if limit is None:
        data = r.content.decode('utf-8')
    else:
        data = '\n'.join(b.decode('utf-8') for b in islice(r.iter_lines(), 0, 1 + limit))

    raw_df = pd.read_csv(io.StringIO(data))

    return prepare_raw_market_prices(raw_df)


def save_market_prices(when, where, output, fformat):
    if when == 'hoy':
        url = 'http://www.sicsantacruz.com/sic/sic2014/pref_sc_hoy_export.php'
    else:
        url = 'http://www.sicsantacruz.com/sic/sic2014/pref_{WHERE}_{WHEN}_ano_export.php'.format(WHERE=where,
                                                                                                  WHEN=when)

    if output is None:
        output_file = 'precios_' + where + '_' + when + '.' + fformat
    else:
        output_file = output

    params = {'type': fformat, 'records': 'all'}
    headers = {'Content-type': 'application/x-www-form-urlencoded'}

    try:
        print('Requesting data for ' + where + ' in ' + when + ' from:\n' + url)

        r = requests.post(url, data=params, headers=headers)

        if r.status_code == 200:
            print('Writing output to ' + output_file)

            with open(output_file, 'wt') as the_file:
                the_file.write(r.content.decode('utf-8'))
        elif r.status_code == 404:
            print('No data for ' + where + ' in ' + when)
    except Exception as e:
        print('Something went wrong :(')
        print(traceback.format_exc())
