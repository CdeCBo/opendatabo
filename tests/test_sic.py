import numpy as np
import pandas as pd
import pytest

from opendatabo.sic import get_market_prices, make_market_prices_url, City, Today, Year, DataNotAvailableException, \
    parse_column_units


EXPECTED_COLS = {'procedencia', 'observaciones',
                 'precio_mayorista_val', 'precio_mayorista_unit_val', 'precio_mayorista_unit_name',
                 'precio_minorista_val', 'precio_minorista_unit_val', 'precio_minorista_unit_name',
                 }


def test_make_market_prices_url():
    assert make_market_prices_url(City.SANTA_CRUZ, Today()) \
           == 'http://www.sicsantacruz.com/sic/sic2014/pref_sc_hoy_export.php'

    assert make_market_prices_url(City.SANTA_CRUZ, Year(2010)) \
           == 'http://www.sicsantacruz.com/sic/sic2014/pref_sc_2010_ano_export.php'


def test_get_scz_2008():
    df = get_market_prices(City.SANTA_CRUZ, Year(2008))

    assert set(df.columns).issuperset(EXPECTED_COLS)
    assert df.shape[0] == 481


@pytest.mark.skip(reason='Fails on weekends and holidays :/')
def test_get_scz_today():
    df = get_market_prices(City.SANTA_CRUZ, Today())

    assert set(df.columns).issuperset(EXPECTED_COLS)


def test_get_scz_2008_limit_42():
    df = get_market_prices(City.SANTA_CRUZ, Year(2008), limit=42)

    assert set(df.columns).issuperset(EXPECTED_COLS)
    assert df.shape[0] == 42


def test_get_scz_2015():
    with pytest.raises(DataNotAvailableException):
        get_market_prices(City.SANTA_CRUZ, Year(2015))


def test_market_uniform_columns():
    for city in City.all():
        for year in Year.all_valid():
            try:
                df = get_market_prices(city, year, limit=5)
            except DataNotAvailableException:
                continue

            assert df.index.names == ['fecha', 'producto', 'variedad']
            assert set(df.columns).issuperset(EXPECTED_COLS)


def test_parse_column_units():
    x, u_v, u_k = parse_column_units(pd.Series(['1 Bs.-/Unidad', np.nan, np.nan]))

    assert x.fillna(-1).tolist() == [1.0, -1, -1]
    assert u_v.fillna(-1).tolist() == [1.0, -1, -1]
    assert u_k.fillna('').tolist() == ['unit', '', '']


@pytest.mark.skip(reason='takes too long')
def test_market_units():
    all_units = set()

    for city in City.all():
        for year in Year.all_valid():
            try:
                df = get_market_prices(city, year)
            except DataNotAvailableException:
                continue

            print(city, year)

            for s in df['precio_mayorista']:
                try:
                    all_units.add(s.split('/')[1])
                except:
                    pass

            for s in df['precio_minorista']:
                try:
                    all_units.add(s.split('/')[1])
                except:
                    pass

    pd.DataFrame({'unit': list(all_units)}).to_csv('units.csv')
