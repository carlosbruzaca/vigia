def calculate_runway(cash: float, daily_burn: float) -> float:
    if daily_burn <= 0:
        return 999
    return cash / daily_burn


def calculate_daily_burn(fixed_cost_avg: float, avg_daily_revenue: float, variable_cost_percent: float) -> float:
    return (fixed_cost_avg / 30) + (avg_daily_revenue * variable_cost_percent / 100)


def calculate_monthly_burn(fixed_cost_avg: float, avg_daily_revenue: float, variable_cost_percent: float) -> float:
    daily_burn = calculate_daily_burn(fixed_cost_avg, avg_daily_revenue, variable_cost_percent)
    return daily_burn * 30


def get_alert_level(days_of_cash: int) -> tuple[str, str]:
    if days_of_cash <= 10:
        return "🔴", "crítico"
    elif days_of_cash <= 20:
        return "⚠️", "atenção"
    else:
        return "✅", "normal"
