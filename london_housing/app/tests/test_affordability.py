from app.calculators import monthly_repayment


def test_monthly_repayment_known_amortization():
    # £200,000 loan, 4.5% annual rate, 25-year term — standard amortization formula
    payment = monthly_repayment(200_000, 4.5, 25)
    assert round(payment, 2) == 1111.66


def test_monthly_repayment_zero_rate_is_simple_division():
    payment = monthly_repayment(120_000, 0, 10)
    assert round(payment, 2) == 1000.00


def test_monthly_repayment_scales_with_principal():
    small = monthly_repayment(100_000, 4.5, 25)
    large = monthly_repayment(200_000, 4.5, 25)
    assert round(large, 2) == round(small * 2, 2)
