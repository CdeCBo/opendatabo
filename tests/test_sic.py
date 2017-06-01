import os

from opendatabo.sic import save_market_prices


def test_save_scz_2008():
    save_market_prices('2008', 'sc', '/tmp/hello.csv', 'csv')

    assert os.path.exists('/tmp/hello.csv')
