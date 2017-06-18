import argparse
import io

import ckanapi
import pandas as pd
import structlog

from opendatabo.common import DataNotAvailableException
from opendatabo.sic import City, Year, get_market_prices

_logger = structlog.get_logger()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Export data from SIC's website to a file")

    parser.add_argument('--host', type=str, required=True,
                        help='Hostname of the target CKAN node')
    parser.add_argument('-k', '--key', type=str,
                        help='API Key for said host')
    parser.add_argument('-p', '--package', type=str, required=True,
                        help='Target package (dataset) ID where the resource will be created')
    parser.add_argument('-r', '--resource', type=str, required=True,
                        help='Target resource name')

    args = parser.parse_args()

    ckan = ckanapi.RemoteCKAN('http://' + args.host, apikey=args.key)

    for city in City.all():
        parts = []

        for year in Year.all_valid():
            try:
                _logger.info('fetching data', city=city, year=year)
                df = get_market_prices(city, year)
                _logger.info('data fetched', city=city, year=year, rows=df.shape[0])
                parts.append(df)

            except DataNotAvailableException as e:
                _logger.warning('fetch fail', city=city, year=year, error=e)
                continue

        full_df = pd.concat(parts)  # type: pd.DataFrame
        full_df.sort_index(inplace=True)

        data = io.StringIO()
        full_df.to_csv(data)
        data_size = data.tell()
        data.seek(0)

        _logger.info('data ready', city=city, rows=full_df.shape[0], data_size=data_size)

        try:
            package = ckan.action.package_show(id=args.package)

            full_resource_name = '{} {}'.format(args.resource, city.name)

            filename = 'sic_{}.csv'.format(city.name)

            resources = list(filter(lambda r: r['name'] == full_resource_name, package['resources']))

            if len(resources) > 2:
                _logger.error('more than one matching resources found')
                exit(1)

            if len(resources) == 0:
                # Creating
                _logger.info('creating resource', name=full_resource_name)
                res = ckan.action.resource_create(package_id=args.package,
                                                  format='csv',
                                                  name=full_resource_name,
                                                  upload=(filename, data),
                                                  )
            else:
                # Updating
                resource_id = resources[0]['id']

                _logger.info('updating resource', name=full_resource_name, id=resource_id)
                res = ckan.action.resource_update(id=resource_id,
                                                  upload=(filename, data),
                                                  )
            _logger.info('saved', resource=res)

        except ckanapi.errors.NotFound:
            _logger.error('package does not exist')
            exit(1)

        except ckanapi.errors.CKANAPIError as e:
            _logger.error('ckan api fail', error=e)
            exit(1)
