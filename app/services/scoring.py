import math

EARTH_RADIUS_KM = 6371.0  # 地球の半径（キロメートル）


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """2点の緯度・経度から、地表に沿った距離（km）を返す（ハーバーサインの公式）"""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) **2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def route_length_km(points: list[tuple[float, float]]) -> float:
    """点のリストから、道のり（隣り合う点どうしの距離の合計, km）を返す）"""
    total = 0.0
    for i in range(len(points) - 1):
        lat1, lon1 = points[i]
        lat2, lon2 = points[i + 1]
        total += distance_km(lat1, lon1, lat2, lon2)
    return total
