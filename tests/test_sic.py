import os

from opendatabo.sic import save_market_prices


def test_save_scz_2014():
    save_market_prices('2014', 'sc', '/tmp/hello.csv', 'csv')

    assert os.path.exists('/tmp/hello.csv')
