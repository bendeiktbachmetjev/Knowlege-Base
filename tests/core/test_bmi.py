import pytest
from app.services.core.bmi import calculate_bmi

def test_bmi_normal():
    assert calculate_bmi(70, 175) == pytest.approx(22.86, 0.01)

def test_bmi_zero_height():
    with pytest.raises(ValueError):
        calculate_bmi(70, 0)

def test_bmi_negative_weight():
    with pytest.raises(ValueError):
        calculate_bmi(-10, 175) 