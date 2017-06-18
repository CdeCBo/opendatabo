import argparse

import ckanapi
import io
import structlog

from opendatabo.cruzero import get_all_bus_line_ids, get_bus_line, bus_lines_to_geojson

_logger = structlog.get_logger()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Export data from SIC's website to a file")

    parser.add_argument('--host', type=str, default='ec2-52-34-181-186.us-west-2.compute.amazonaws.com',
                        help='Hostname of the target CKAN node')
    parser.add_argument('-k', '--key', type=str,
                        help='API Key for said host')
    parser.add_argument('-p', '--package', type=str, required=True,
                        help='Target package (dataset) ID where the resource will be created')
    parser.add_argument('-r', '--resource', type=str, required=True,
                        help='Target resource name')
    parser.add_argument('-n', '--name', type=str, default='lineas-de-buses.json',
                        help='Filename for upload')

    args = parser.parse_args()

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

    ckan = ckanapi.RemoteCKAN('http://' + args.host, apikey=args.key)

    try:
        package = ckan.action.package_show(id=args.package)

        resources = list(filter(lambda r: r['name'] == args.resource, package['resources']))

        if len(resources) > 2:
            _logger.error('more than one matching resources found')
            exit(1)

        if len(resources) == 0:
            # Creating
            _logger.info('creating resource')
            res = ckan.action.resource_create(package_id=args.package,
                                              format='geojson',
                                              name=args.resource,
                                              upload=(args.name, io.StringIO(data)),
                                              )
        else:
            # Updating
            _logger.info('updating resource')
            res = ckan.action.resource_update(id=resources[0]['id'],
                                              upload=(args.name, io.StringIO(data)),
                                              )

        _logger.info('saved', resource=res)

    except ckanapi.errors.NotFound:
        _logger.error('package does not exist')
        exit(1)

    except ckanapi.errors.CKANAPIError as e:
        _logger.error('ckan api fail', error=e)
        exit(1)
