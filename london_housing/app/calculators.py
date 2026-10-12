def monthly_repayment(principal: float, annual_rate: float, term_years: int) -> float:
    r = annual_rate / 100 / 12
    n = term_years * 12
    if r == 0:
        return principal / n
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def max_affordable_rent(monthly_income: float, ratio: float = 0.35) -> float:
    """Standard rule of thumb: rent shouldn't exceed `ratio` of gross monthly income."""
    return monthly_income * ratio
