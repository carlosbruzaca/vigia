import pytest
from src.utils.burn_rate import calculate_runway, calculate_monthly_burn
from src.utils.formatters import format_currency, format_runway, format_company_status


class TestBurnRate:
    def test_calculate_runway(self):
        assert calculate_runway(10000, 1000) == 10
        assert calculate_runway(5000, 500) == 10
        assert calculate_runway(0, 1000) == 0

    def test_calculate_runway_zero_burn(self):
        result = calculate_runway(10000, 0)
        assert result == float("inf")

    def test_calculate_monthly_burn(self):
        entries = [
            {"amount": 1000, "entry_type": "expense"},
            {"amount": 500, "entry_type": "expense"},
            {"amount": 2000, "entry_type": "income"},
        ]
        assert calculate_monthly_burn(entries) == 1500


class TestFormatters:
    def test_format_currency(self):
        assert format_currency(1000) == "R$ 1.000,00"
        assert format_currency(1000.50) == "R$ 1.000,50"

    def test_format_runway(self):
        assert format_runway(10.5) == "10.5 meses"
        assert format_runway(float("inf")) == "∞ meses"

    def test_format_company_status(self):
        company = {"name": "Teste", "cash": 10000}
        result = format_company_status(company, 1000, 10)
        assert "Teste" in result
        assert "R$ 10.000,00" in result
        assert "R$ 1.000,00/mês" in result
