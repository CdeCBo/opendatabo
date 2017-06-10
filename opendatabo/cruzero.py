import re
from decimal import Decimal
from operator import itemgetter
from typing import List

import geojson
import requests

from opendatabo.common import DataNotAvailableException


class GeoJSONEncoderWithDecimal(geojson.GeoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(GeoJSONEncoderWithDecimal, self).default(obj)


class LatLng:
    def __init__(self, lat: Decimal, lng: Decimal):
        self.lat = lat
        self.lng = lng

    def __repr__(self):
        return 'LatLng({!r}, {!r})'.format(self.lat, self.lng)

    def to_pair(self):
        return self.lat, self.lng


class BusLine:
    def __init__(self, line_id: int, name: str, speed: Decimal, distance: Decimal, total_time: Decimal, points: List[LatLng]):
        self.line_id = line_id
        self.name = name
        self.speed = speed
        self.distance = distance
        self.total_time = total_time
        self.points = points

    def to_geojson(self):
        return geojson.dumps(self, cls=GeoJSONEncoderWithDecimal)

    def iter_coords(self):
        for point in self.points:
            yield point.to_pair()

    @property
    def __geo_interface__(self):
        props = self.__dict__.copy()
        del props['points']
        geometry = geojson.LineString(list(self.iter_coords()))
        return geojson.Feature(id=self.line_id, geometry=geometry, properties=props)


def get_bus_line(line_id: int) -> BusLine:
    url = 'http://cruzero.net/cruzero/lineasbuses/json_rutas?lbsId={}'.format(line_id)

    r = requests.get(url)

    try:
        data = r.json()
    except ValueError:
        raise DataNotAvailableException()

    points: List[LatLng] = []

    bus_line = BusLine(line_id=line_id,
                       name=data['infoLinea']['lbsNombre'],
                       speed=Decimal(data['infoLinea']['lbsVelocidad']),
                       distance=Decimal(data['infoLinea']['lbsDistancia']),
                       total_time=Decimal(data['infoLinea']['lbsTiempo']),
                       points=points,
                       )

    for point_data in data['lineasbusesruta']:
        points.append(LatLng(lat=Decimal(point_data['lbrLatitud']),
                             lng=Decimal(point_data['lbrLongitud']),
                             ))

    return bus_line


def get_all_bus_line_ids() -> List[int]:
    url = 'http://cruzero.net/cruzero/lineasbuses'

    html = requests.get(url).text

    result = []

    for match in re.findall(r'mostrarLinea\((\d+),', html):
        result.append(int(match))

    return result


def get_all_bus_lines() -> List[BusLine]:
    return list(map(get_bus_line, get_all_bus_line_ids()))
