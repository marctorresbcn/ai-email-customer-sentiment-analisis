"""Tests para query_builder.py"""

from datetime import datetime, timedelta

import pytest

from query_builder import GmailQueryBuilder


class TestGmailQueryBuilder:
    """Test suite para GmailQueryBuilder."""

    def test_empty_query(self):
        """Test: query vacía sin condiciones."""
        qb = GmailQueryBuilder()
        assert qb.build() == ""

    def test_base_query(self):
        """Test: query base inicial."""
        qb = GmailQueryBuilder(base_query="is:unread")
        assert "is:unread" in qb.build()

    def test_add_from_date_valid(self):
        """Test: agregar fecha 'desde'."""
        qb = GmailQueryBuilder()
        qb.add_from_date("2026-03-01")
        assert "after:2026/03/01" in qb.build()

    def test_add_from_date_invalid(self):
        """Test: fecha 'desde' con formato inválido."""
        qb = GmailQueryBuilder()
        with pytest.raises(ValueError, match="Fecha inválida"):
            qb.add_from_date("01-03-2026")

    def test_add_date_range_valid(self):
        """Test: agregar rango de fechas válido."""
        qb = GmailQueryBuilder()
        qb.add_date_range("2026-03-01", "2026-03-31")
        result = qb.build()
        assert "after:2026/03/01" in result
        assert "before:2026/03/31" in result

    def test_add_date_range_invalid_from_date(self):
        """Test: fecha 'desde' inválida en rango."""
        qb = GmailQueryBuilder()
        with pytest.raises(ValueError, match="Fechas inválidas"):
            qb.add_date_range("invalid", "2026-03-31")

    def test_add_date_range_invalid_to_date(self):
        """Test: fecha 'hasta' inválida en rango."""
        qb = GmailQueryBuilder()
        with pytest.raises(ValueError, match="Fechas inválidas"):
            qb.add_date_range("2026-03-01", "invalid")

    def test_add_preset_range_last_week(self):
        """Test: rango predefinido 'última semana'."""
        qb = GmailQueryBuilder()
        qb.add_preset_range("last_week")
        result = qb.build()
        assert "after:" in result

    def test_add_preset_range_last_month(self):
        """Test: rango predefinido 'último mes'."""
        qb = GmailQueryBuilder()
        qb.add_preset_range("last_month")
        result = qb.build()
        assert "after:" in result

    def test_add_preset_range_last_three_months(self):
        """Test: rango predefinido 'últimos 3 meses'."""
        qb = GmailQueryBuilder()
        qb.add_preset_range("last_three_months")
        result = qb.build()
        assert "after:" in result

    def test_add_preset_range_last_year(self):
        """Test: rango predefinido 'último año'."""
        qb = GmailQueryBuilder()
        qb.add_preset_range("last_year")
        result = qb.build()
        assert "after:" in result

    def test_add_preset_range_invalid(self):
        """Test: rango predefinido inválido."""
        qb = GmailQueryBuilder()
        with pytest.raises(ValueError, match="Preset inválido"):
            qb.add_preset_range("invalid_preset")

    def test_add_recipient_valid(self):
        """Test: agregar destinatario válido."""
        qb = GmailQueryBuilder()
        qb.add_recipient("alias@empresa.com")
        assert "to:alias@empresa.com" in qb.build()

    def test_add_recipient_invalid(self):
        """Test: email de destinatario inválido."""
        qb = GmailQueryBuilder()
        with pytest.raises(ValueError, match="Email inválido"):
            qb.add_recipient("invalid-email")

    def test_chaining(self):
        """Test: encadenamiento de métodos."""
        qb = GmailQueryBuilder()
        result = (
            qb.add_from_date("2026-03-01")
            .add_recipient("support@empresa.com")
            .build()
        )
        assert "after:2026/03/01" in result
        assert "to:support@empresa.com" in result

    def test_multiple_conditions(self):
        """Test: múltiples condiciones combinadas."""
        qb = GmailQueryBuilder(base_query="is:unread")
        qb.add_date_range("2026-03-01", "2026-03-31")
        qb.add_recipient("support@empresa.com")
        result = qb.build()
        assert "is:unread" in result
        assert "after:2026/03/01" in result
        assert "before:2026/03/31" in result
        assert "to:support@empresa.com" in result

    def test_preset_range_date_calculation(self):
        """Test: verificar que los cálculos de fechas son correctos."""
        qb = GmailQueryBuilder()
        qb.add_preset_range("last_week")
        result = qb.build()
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        expected_date = week_ago.strftime("%Y/%m/%d")
        assert f"after:{expected_date}" in result

    def test_add_keywords_single(self):
        """Test: agregar una palabra clave."""
        qb = GmailQueryBuilder()
        qb.add_keywords(["pedidos"])
        result = qb.build()
        assert 'subject:"pedidos"' in result

    def test_add_keywords_multiple(self):
        """Test: agregar múltiples palabras clave."""
        qb = GmailQueryBuilder()
        qb.add_keywords(["pedidos", "devoluciones", "tallas"])
        result = qb.build()
        assert 'subject:"pedidos"' in result
        assert 'subject:"devoluciones"' in result
        assert 'subject:"tallas"' in result
        assert " OR " in result

    def test_add_keywords_empty_list(self):
        """Test: lista vacía de palabras clave."""
        qb = GmailQueryBuilder()
        qb.add_keywords([])
        assert qb.build() == ""

    def test_add_keywords_with_spaces(self):
        """Test: palabras clave con espacios en blanco."""
        qb = GmailQueryBuilder()
        qb.add_keywords(["  exchange  ", "returns"])
        result = qb.build()
        assert 'subject:"exchange"' in result
        assert 'subject:"returns"' in result

    def test_add_keywords_lowercase_normalization(self):
        """Test: las palabras clave se normalizan a minúsculas."""
        qb = GmailQueryBuilder()
        qb.add_keywords(["PEDIDOS", "Devoluciones"])
        result = qb.build()
        assert 'subject:"pedidos"' in result
        assert 'subject:"devoluciones"' in result

    def test_keywords_combined_with_other_filters(self):
        """Test: palabras clave combinadas con otros filtros."""
        qb = GmailQueryBuilder()
        qb.add_from_date("2026-03-01").add_keywords(["pedidos", "devoluciones"]).add_recipient("support@empresa.com")
        result = qb.build()
        assert "after:2026/03/01" in result
        assert 'subject:"pedidos"' in result
        assert 'subject:"devoluciones"' in result
        assert "to:support@empresa.com" in result
