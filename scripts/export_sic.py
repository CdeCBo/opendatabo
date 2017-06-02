import argparse

from opendatabo.sic import save_market_prices
from opendatabo.sic import City, Year, Today


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Export data from SIC's website to a file")

    # TODO: Kill format argument
    parser.add_argument('-c', '--clean', action='store_false', help='Give a better structure to the data')
    parser.add_argument('-f', '--format', type=str, default='csv', help='File format to request',
                        choices=['csv', 'xml'])
    parser.add_argument('-l', '--location', type=str, default='sc', help="City code, known values are [sc, trd, cbb]")
    parser.add_argument('-o', '--output', type=str, help='Output file')
    parser.add_argument('-w', '--when', type=str, default='hoy', help="Year for the dataset you want")

    args = parser.parse_args()

    if args.when == 'hoy':
        timeframe = Today()
    else:
        timeframe = Year(int(args.when))
    save_market_prices(City(args.location), timeframe, args.format, args.clean, args.output)
