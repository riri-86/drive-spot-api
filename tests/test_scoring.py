import pytest

from app.services.scoring import (
    bearing_deg,
    curve_deg_per_km,
    curve_deg_per_km_by_steps,
    detour_ratio,
    distance_km,
    route_length_km,
    strait_distance_km,
    turn_angle_deg,
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


def test_turn_angle_same_bearing_is_0():
    assert turn_angle_deg(45, 45) == 0


def test_turn_angle_opposite_bearing_is_180():
    assert turn_angle_deg(10, 190) ==180


def test_turn_angle_simple_difference():
    assert turn_angle_deg(10, 30) == 20


def test_turn_angle_across_north():
    assert turn_angle_deg(350, 10) == 20


def test_turn_angle_left_and_right_are_same():
    assert turn_angle_deg(10, 30) == turn_angle_deg(30, 10)


def test_curve_two_points_is_0():
    east = (OSAKA[0], OSAKA[1] + 0.01)
    assert curve_deg_per_km([OSAKA, east]) == 0


def test_curve_straight_line_is_0():
    east1 = (OSAKA[0], OSAKA[1] + 0.01)
    east2 = (OSAKA[0], OSAKA[1] + 0.02)
    assert curve_deg_per_km([OSAKA, east1, east2]) == pytest.approx(0, abs=0.01)


def test_curve_one_right_angle_turn():
    north = (OSAKA[0] + 0.01, OSAKA[1])
    north_east = (OSAKA[0] + 0.01, OSAKA[1] + 0.01)
    points = [OSAKA, north, north_east]
    assert curve_deg_per_km(points) == pytest.approx(90 / route_length_km(points), abs=0.1)


def test_curve_ignores_duplicate_points():
    north = (OSAKA[0] + 0.01, OSAKA[1])
    north_east = (OSAKA[0] + 0.01, OSAKA[1] + 0.01)
    without_dup = curve_deg_per_km([OSAKA, north, north_east])
    with_dup = curve_deg_per_km([OSAKA, north, north, north_east])
    assert with_dup == pytest.approx(without_dup)


def test_curve_one_point_raises_error():
    with pytest.raises(ValueError):
        curve_deg_per_km([OSAKA])


def test_curve_by_steps_ignores_turn_at_step_boundary():
    north1 = (OSAKA[0] + 0.01, OSAKA[1])
    north2 = (OSAKA[0] + 0.02, OSAKA[1])
    east1 = (north2[0], north2[1] + 0.01)
    east2 = (north2[0], north2[1] + 0.02)
    steps_points = [[OSAKA, north1, north2], [north2, east1, east2]]
    assert curve_deg_per_km_by_steps(steps_points) == pytest.approx(0, abs=0.01)


def test_curve_by_steps_weights_by_length():
    north = (OSAKA[0] + 0.01, OSAKA[1])
    north2 = (OSAKA[0] + 0.02, OSAKA[1])
    north2_east = (north2[0], north2[1] + 0.01)
    straight_step = [OSAKA, north]
    turn_step = [north, north2, north2_east]
    expected = 90 / (route_length_km(straight_step) + route_length_km(turn_step))
    assert curve_deg_per_km_by_steps([straight_step, turn_step]) == pytest.approx(expected,abs=0.1)


def test_curve_by_steps_skips_zero_length_step():
    north = (OSAKA[0] + 0.01, OSAKA[1])
    north_east = (OSAKA[0] + 0.01, OSAKA[1] + 0.01)
    points = [OSAKA,north, north_east]
    assert curve_deg_per_km_by_steps([points, [north_east]]) == pytest.approx(curve_deg_per_km(points))


def test_curve_by_steps_allzero_length_raises_error():
    with pytest.raises(ValueError):
        curve_deg_per_km_by_steps([[OSAKA],[OSAKA, OSAKA]])
