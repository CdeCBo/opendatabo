from operator import itemgetter

import pytest

from opendatabo.sic import get_market_prices, make_market_prices_url, City, Today, Year, DataNotAvailableException


def test_make_market_prices_url():
    assert make_market_prices_url(City.SANTA_CRUZ, Today()) \
           == 'http://www.sicsantacruz.com/sic/sic2014/pref_sc_hoy_export.php'

    assert make_market_prices_url(City.SANTA_CRUZ, Year(2010)) \
           == 'http://www.sicsantacruz.com/sic/sic2014/pref_sc_2010_ano_export.php'


def test_get_scz_2008():
    df = get_market_prices(City.SANTA_CRUZ, Year(2008))

    assert set(df.columns).issuperset({'procedencia', 'precio_mayorista', 'precio_minorista', 'observaciones'})
    assert df.shape[0] == 481

def test_get_scz_today():
    df = get_market_prices(City.SANTA_CRUZ, Today())

    assert set(df.columns) == {'Mercado', 'procedencia', 'precio_mayorista', 'precio_minorista', 'observaciones'}


def test_get_scz_2008_limit_42():
    df = get_market_prices(City.SANTA_CRUZ, Year(2008), limit=42)

    assert set(df.columns).issuperset({'procedencia', 'precio_mayorista', 'precio_minorista', 'observaciones'})
    assert df.shape[0] == 42


def test_get_scz_2015():
    with pytest.raises(DataNotAvailableException):
        get_market_prices(City.SANTA_CRUZ, Year(2015))


def test_market_uniform_columns():
    expected_cols = {'procedencia', 'precio_mayorista', 'precio_minorista', 'observaciones'}

    for city in City.all():
        for year in Year.all_valid():
            try:
                df = get_market_prices(city, year, limit=5)
            except DataNotAvailableException:
                continue

            assert df.index.names == ['fecha', 'producto', 'variedad']
            assert set(df.columns).issuperset(expected_cols)


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

    import pandas as pd
    pd.DataFrame({'unit': list(all_units)}).to_csv('units.csv')
