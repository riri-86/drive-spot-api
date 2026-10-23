import pytest

from app.services.scoring import distance_km, route_length_km

OSAKA = (34.7025, 135.4959)
NAGOYA = (35.1709, 136.8815)
TOKYO = (35.6812, 139.7671)

def test_distance_same_point_is_zero():
    assert distance_km(34.70, 135.50, 34.70, 135.50) == 0


def test_distance_osaka_to_tokyo():
    result = distance_km(34.7025, 135.4959, 35.6812, 139.7671)
    assert result == pytest.approx(403, abs=1)


def test_distance_is_same_in_both_directions():
    go = distance_km(34.7025, 135.4959, 35.6812, 139.7671)
    back = distance_km(35.6812, 139.7671, 34.7025, 135.4959)
    assert go == pytest.approx(back)


def test_route_length_single_point_is_zero():
    assert route_length_km([OSAKA]) == 0


def test_route_length_same_points_is_zero():
    assert route_length_km([OSAKA, OSAKA, OSAKA]) == 0


def test_route_length_two_points_equals_distance():
    assert route_length_km([OSAKA, TOKYO]) == pytest.approx(distance_km(*OSAKA, *TOKYO))


def test_route_length_is_sum_of_sections():
    expected = distance_km(*OSAKA, *NAGOYA) + distance_km(*NAGOYA, *TOKYO)
    assert route_length_km([OSAKA,NAGOYA,TOKYO]) == pytest.approx(expected)


def test_route_length_is_same_when_reversed():
    go = route_length_km([OSAKA, NAGOYA, TOKYO])
    back = route_length_km([TOKYO, NAGOYA, OSAKA])
    assert go == pytest.approx(back)
