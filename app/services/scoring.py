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


def strait_distance_km(points: list[tuple[float, float]]) -> float:
    """出発地（最初の点）と目的地（最後の点）の直線距離（km）を返す"""
    return distance_km(*points[0], *points[-1])


def detour_ratio(points: list[tuple[float, float]]) -> float:
    """迂回率（道のり ÷ 直線距離）を返す"""
    strait = strait_distance_km(points)
    if strait == 0:
        raise ValueError("出発地と目的地が同じ地点のため、迂回率を計算できません")
    return route_length_km(points) / strait


def bearing_deg(lat1: float, lon1: float, lat2:float, lon2: float) -> float:
    """点1から点2へ向かう方位角（北を0度として時計回り、0以上360未満を返す"""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)

    x = math.sin(dlon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
    return math.degrees(math.atan2(x,y)) % 360