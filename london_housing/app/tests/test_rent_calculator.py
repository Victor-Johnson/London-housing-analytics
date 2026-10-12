from app.calculators import max_affordable_rent, rent_budget_from_amount


def test_max_affordable_rent_default_ratio():
    assert max_affordable_rent(4000) == 1400.0  # 35% of £4,000


def test_max_affordable_rent_custom_ratio():
    assert max_affordable_rent(4000, ratio=0.3) == 1200.0


def test_max_affordable_rent_scales_linearly():
    assert max_affordable_rent(8000) == max_affordable_rent(4000) * 2


def test_rent_budget_from_amount_with_no_bills():
    assert rent_budget_from_amount(1000) == 1000


def test_rent_budget_from_amount_subtracts_bills():
    assert rent_budget_from_amount(1000, monthly_bills=250) == 750


def test_rent_budget_from_amount_never_goes_negative():
    assert rent_budget_from_amount(200, monthly_bills=500) == 0
