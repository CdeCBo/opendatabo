from opendatabo.sic import get_market_prices, make_market_prices_url, City, Today, Year


def test_make_market_prices_url():
    assert make_market_prices_url(City.SANTA_CRUZ, Today()) \
           == 'http://www.sicsantacruz.com/sic/sic2014/pref_sc_hoy_export.php'

    assert make_market_prices_url(City.SANTA_CRUZ, Year(2010)) \
           == 'http://www.sicsantacruz.com/sic/sic2014/pref_sc_2010_ano_export.php'


def test_get_scz_2008():
    df = get_market_prices(City.SANTA_CRUZ, Year(2008))

    assert df.columns.tolist() == ['producto', 'variedad', 'Nom_Procedencia', 'Precio Mayorista', 'Precio Minorista',
                                   'observaciones', 'fecha']
    assert df.size == 3367
