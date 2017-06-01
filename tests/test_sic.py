import pytest

from opendatabo.sic import get_market_prices, make_market_prices_url, City, Today, Year, DataNotAvailableException


def test_make_market_prices_url():
    assert make_market_prices_url(City.SANTA_CRUZ, Today()) \
           == 'http://www.sicsantacruz.com/sic/sic2014/pref_sc_hoy_export.php'

    assert make_market_prices_url(City.SANTA_CRUZ, Year(2010)) \
           == 'http://www.sicsantacruz.com/sic/sic2014/pref_sc_2010_ano_export.php'


def test_get_scz_2008():
    df = get_market_prices(City.SANTA_CRUZ, Year(2008))

    assert set(df.columns) == {'producto', 'variedad', 'procedencia',
                               'precio_mayorista', 'precio_minorista',
                               'observaciones', 'fecha'}
    assert df.size == 3367


def test_get_scz_2015():
    with pytest.raises(DataNotAvailableException):
        get_market_prices(City.SANTA_CRUZ, Year(2015))


def test_market_uniform_columns():
    expected_cols = {'producto', 'variedad', 'procedencia',
                     'precio_mayorista', 'precio_minorista',
                     'observaciones', 'fecha'}

    for city in City.all():
        for year in Year.all_valid():
            try:
                df = get_market_prices(city, year, limit=5)
            except DataNotAvailableException:
                continue

            assert set(df.columns).issuperset(expected_cols)
