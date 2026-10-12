from app.calculators import max_affordable_rent


def test_max_affordable_rent_default_ratio():
    assert max_affordable_rent(4000) == 1400.0  # 35% of £4,000


def test_max_affordable_rent_custom_ratio():
    assert max_affordable_rent(4000, ratio=0.3) == 1200.0


def test_max_affordable_rent_scales_linearly():
    assert max_affordable_rent(8000) == max_affordable_rent(4000) * 2
