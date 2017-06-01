import argparse

from opendatabo.sic import save_market_prices


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Export data from SIC's website to a file")

    # Not an FB plug
    parser.add_argument('-f', '--format', type=str, default='csv', help='File format to request',
                        choices=['csv', 'xml'])
    parser.add_argument('-l', '--location', type=str, default='sc', help="City code, known values are [sc, trd, cbb]")
    parser.add_argument('-o', '--output', type=str, help='Output file')
    parser.add_argument('-w', '--when', type=str, default='hoy', help="Year for the dataset you want")

    args = parser.parse_args()

    save_market_prices(args.when, args.location, args.output, args.format)
