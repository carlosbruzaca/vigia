def format_currency(amount: float | None) -> str:
    if amount is None:
        amount = 0
    return f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_days(days: float) -> str:
    if days >= 999:
        return "∞"
    return f"{days:.0f}"


def format_percentage(value: float | None) -> str:
    if value is None:
        value = 0
    return f"{value:.1f}%"


def format_daily_report(
    company_name: str,
    revenue_yesterday: float,
    revenue_avg: float,
    cash_balance: float,
    days_of_cash: int,
    overdue_total: float,
    alert_emoji: str,
    alert_level: str
) -> str:
    variation = 0
    if revenue_avg > 0:
        variation = ((revenue_yesterday - revenue_avg) / revenue_avg) * 100
    
    variation_emoji = "📈" if variation > 0 else "📉" if variation < 0 else "➡️"
    
    message = f"📊 *Relatório Diário - {company_name}*\n\n"
    
    message += f"{alert_emoji} Status: {alert_level}\n\n"
    
    message += f"💰 *Caixa Atual:* {format_currency(cash_balance)}\n"
    message += f"⏱️ *Dias de Caixa:* {format_days(days_of_cash)} dias\n\n"
    
    message += f"📈 *Faturamento:*\n"
    message += f"  Ontem: {format_currency(revenue_yesterday)}\n"
    message += f"  Média (7d): {format_currency(revenue_avg)}\n"
    message += f"  {variation_emoji} Variação: {variation:+.1f}%\n"
    
    if overdue_total > 0:
        message += f"\n⚠️ *Clientes em Atraso:* {format_currency(overdue_total)}\n"
    
    return message


def format_simple_report(
    company_name: str,
    cash_balance: float,
    daily_burn: float,
    days_of_cash: int,
    alert_emoji: str,
    alert_level: str
) -> str:
    message = f"📊 *{company_name}*\n\n"
    message += f"{alert_emoji} {alert_level}\n\n"
    message += f"💰 Caixa: {format_currency(cash_balance)}\n"
    message += f"🔥 Burn: {format_currency(daily_burn)}/dia\n"
    message += f"⏱️ Dias restantes: {format_days(days_of_cash)}"
    return message
