def format_currency(amount: float) -> str:
    return f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_runway(months: float) -> str:
    if months == float("inf"):
        return "∞ meses"
    return f"{months:.1f} meses"


def format_company_status(company: dict, burn_rate: float, runway: float) -> str:
    return (
        f"🏢 *{company.get('name', 'Empresa')}*\n\n"
        f"💰 Caixa: {format_currency(company.get('cash', 0))}\n"
        f"🔥 Burn Rate: {format_currency(burn_rate)}/mês\n"
        f"⏱️ Runway: {format_runway(runway)}"
    )
