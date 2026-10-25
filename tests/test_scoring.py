import pytest

from app.services.scoring import (
    bearing_deg,
    detour_ratio,
    distance_km,
    route_length_km,
    strait_distance_km,
)

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


def test_strait_distance_users_first_and_last_points():
    assert strait_distance_km([OSAKA, NAGOYA, TOKYO]) == pytest.approx(distance_km(*OSAKA, *TOKYO))


def test_detour_ratio_two_points_is_one():
    assert detour_ratio([OSAKA,TOKYO]) == pytest.approx(1.0)


def test_detour_ratio_is_at_least_one():
    assert detour_ratio([OSAKA, NAGOYA, TOKYO]) >= 1.0


def test_detour_ratio_same_start_and_goal_raises_error():
    with pytest.raises(ValueError):
        detour_ratio([OSAKA,NAGOYA, OSAKA])


def test_bearing_due_north_is_0():
    north = (OSAKA[0] + 0.01, OSAKA[1])
    assert bearing_deg(*OSAKA, *north) == pytest.approx(0, abs=0.01)


def test_bearing_due_east_is_90():
    east = (OSAKA[0], OSAKA[1] + 0.01)
    assert bearing_deg(*OSAKA, *east) == pytest.approx(90, abs=0.01)


def test_bearing_due_south_is_180():
    south = (OSAKA[0] - 0.01, OSAKA[1])
    assert bearing_deg(*OSAKA,*south) == pytest.approx(180,abs=0.01)


def test_bearing_due_west_is_270():
    west = (OSAKA[0], OSAKA[1] - 0.01)
    assert bearing_deg(*OSAKA, *west) == pytest.approx(270, abs=0.01)


def test_bearing_is_between_0_and_360():
    for start, goal in [(OSAKA, TOKYO), (TOKYO, OSAKA), (NAGOYA, OSAKA)]:
        result = bearing_deg(*start,*goal)
        assert 0 <= result < 360
