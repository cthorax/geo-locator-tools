"""
Coords object definition
"""

from decimal import *
from functools import total_ordering
from math import sin, cos, sqrt, atan2, radians

# approx radius of earth in km
R = 6373.0

# decimal points for coordinates
QUANT = '0.00000001'


@total_ordering
class Coords(object):
    """
    This used to be a named tuple but it grew into this
    if lat / lng are set in kwargs, we expect them to be raw (unquantized) decimals (ie.: Decimal('31.45'))
    We then quantize them to whatever QUANT is set itt during creation, and THAT is our float.
    Values: self.address_string, self.lat, self.lng, self.id (if from DB, else None), self.agendaitem_id
    """
    def __init__(self, c_id=None, **args):
        self.id = c_id

        if self.id:
            # assume we came from a DB query
            self.valid = True
        else:
            self.valid = False

        if args:
            self.lat = Decimal(args.get('lat')).quantize(Decimal(QUANT))
            self.lng = Decimal(args.get('lng')).quantize(Decimal(QUANT))
            self.address_string = args.get('address_string', None)
            self.agendaitem_id = args.get('agendaitem_id', None)
        else:
            self.lat = None
            self.lng = None
            self.address_string = None
            self.agendaitem_id = None

    def coords_tuple(self):
        if self.lat and self.lng:
            return self.lat, self.lng
        else:
            return None

    def __eq__(self, other):
        return self.coords_tuple() == other.coords_tuple()

    def __lt__(self, other):
        # sort by lowest lat - doesn't really matter as long as it's consistent?
        return self.lat < other.lat

    def __repr__(self):
        c_t = self.coords_tuple()
        if c_t:
            return "<Coords {0:.5f} {1:.5f} ({2})>".format(self.lat, self.lng, self.address_string)
        else:
            return "<Coords (empty)>"

    def __hash__(self):
        # required for set comparisons, which is why it's weird.
        if self.address_string and self.lat and self.lng:
            return hash((self.address_string, self.lat, self.lng))
        else:
            return hash(self.__repr__())

    @classmethod
    def create_from_db_query(cls, coords_dict_from_db):
        return cls(coords_dict_from_db['id'], **coords_dict_from_db)

    def validate_for_save(self):
        valid = True
        for attr in ['lat', 'lng', 'address_string', 'agendaitem_id']:
            if not hasattr(self, attr) or getattr(self, attr) is None:
                self.valid = False
                return False
        self.valid = True
        return valid

    def distance_from_coords(self, lat, lng, system='imperial'):
        """
        Given a Coord object, calculates distance from lat, lng
        :param lat:
        :param lng:
        :param system: metric or imperial?
        :return: None on failure, else a float
        """
        # TODO re-do this with coords list
        # lat1 is the ai, lat2 is the param
        if self.lat and self.lng:
            lat1 = radians(self.lat)
            lng1 = radians(self.lng)

            lat2 = radians(lat)
            lng2 = radians(lng)

            dlon = lng2 - lng1
            dlat = lat2 - lat1

            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            distance_km = R * c

            if system == 'imperial':
                return distance_km * 0.62137119
            elif system == 'metric':
                return distance_km
            else:
                return None
        else:
            return None

if __name__ == '__main__':
    a = Coords(c_id=None, lat=30.213381, lng=-97.899124)
    print(a.distance_from_coords(31, 98))
    b = Coords(c_id=12, lat=30.198103, lng=-97.837956)
    print(b)
