from math import asin, cos, radians, sin, sqrt


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in kilometers; stable for coincident/antipodal points."""
    dlat, dlng = radians(lat2 - lat1), radians(lng2 - lng1)
    term = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return 6371.0088 * 2 * asin(sqrt(min(1.0, max(0.0, term))))
