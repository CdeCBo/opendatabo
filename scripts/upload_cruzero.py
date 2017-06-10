import argparse
import datetime

import io
import requests
import structlog
import sys

from opendatabo.cruzero import get_all_bus_line_ids, get_bus_line, bus_lines_to_geojson

_logger = structlog.get_logger()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Export data from SIC's website to a file")

    parser.add_argument('--host', type=str, default='ec2-52-34-181-186.us-west-2.compute.amazonaws.com',
                        help='Hostname of the target CKAN node')
    parser.add_argument('-k', '--key', type=str,
                        help='API Key for said host')
    parser.add_argument('-p', '--package', type=str,
                        help='Target package (dataset) ID where the resource will be created')
    parser.add_argument('--id', type=str,
                        help='Update an existing resource with this ID')
    parser.add_argument('-n', '--name', type=str, default='lineas-de-buses.json',
                        help='Filename for upload')

    args = parser.parse_args()

    if bool(args.package) == bool(args.id):
        print('Specify ONE of --package OR --id', file=sys.stderr)
        exit(1)

    line_ids = get_all_bus_line_ids()
    _logger.info('line_ids', len=len(line_ids))

    bus_lines = []

    for line_id in line_ids:
        try:
            bus_line = get_bus_line(line_id)
            _logger.info('bus_line', id=line_id, name=bus_line.name, points_len=len(bus_line.points))
            bus_lines.append(bus_line)
        except:
            _logger.warning('bus_line failed', id=line_id)

    data = bus_lines_to_geojson(bus_lines)

    if args.id:
        # Updating
        url = 'http://{}/api/action/resource_update'.format(args.host)
        params = {'id': args.id,
                  }
    else:
        # Creating
        url = 'http://{}/api/action/resource_create'.format(args.host)
        params = {'package_id': args.package,
                  'format': 'geojson',
                  'name': 'CZR ' + datetime.date.today().isoformat(),
                  }

    _logger.info('upload start')

    r = requests.post(url,
                      data=params,
                      headers={'X-CKAN-API-Key': args.key},
                      files=[('upload', (args.name, io.StringIO(data)))],
                      )

    if r.status_code != 200:
        _logger.error('save fail', error=r.text)
        exit(1)

    response = r.json()

    if not response['success']:
        _logger.error('save fail', error=response['error'])
        exit(1)

    _logger.info('saved', message=response['result'])
