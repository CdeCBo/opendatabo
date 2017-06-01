import os

from opendatabo.sic import save_market_prices, get_market_prices


def test_get_scz_2008():
    df = get_market_prices('2008', 'sc')

    assert df.columns.tolist() == ['producto', 'variedad', 'Nom_Procedencia', 'Precio Mayorista', 'Precio Minorista',
                                   'observaciones', 'fecha']
    assert df.size == 3367
