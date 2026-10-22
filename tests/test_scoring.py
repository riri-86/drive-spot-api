import pytest

from app.services.scoring import distance_km

def test_distance_same_point_is_zero():
    assert distance_km(34.70, 135.50, 34.70, 135.50) == 0


def test_distance_osaka_to_tokyo():
    result = distance_km(34.7025, 135.4959, 35.6812, 139.7671)
    assert result == pytest.approx(403, abs=1)


def test_distance_is_same_in_both_directions():
    go = distance_km(34.7025, 135.4959, 35.6812, 139.7671)
    back = distance_km(35.6812, 139.7671, 34.7025, 135.4959)
    assert go == pytest.approx(back)
