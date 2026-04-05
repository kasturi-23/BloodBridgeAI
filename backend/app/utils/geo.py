from math import atan2, cos, radians, sin, sqrt

EARTH_RADIUS_KM = 6371.0
MILES_PER_KM = 0.621371


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS_KM * c * MILES_PER_KM
