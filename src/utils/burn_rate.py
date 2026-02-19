def calculate_runway(cash: float, burn_rate: float) -> float:
    if burn_rate <= 0:
        return float("inf")
    return cash / burn_rate


def calculate_monthly_burn(entries: list[dict]) -> float:
    expenses = sum(e.get("amount", 0) for e in entries if e.get("entry_type") == "expense")
    return expenses
