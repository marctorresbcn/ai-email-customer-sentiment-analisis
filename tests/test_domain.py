import pytest
from domain import Email, SentimentResult


class TestEmail:
    """Tests para la entidad Email"""

    def test_email_creation(self):
        """Debe crear un Email correctamente"""
        email = Email(
            id="123",
            thread_id="thread_456",
            sender="cliente@example.com",
            subject="Problema con servicio",
            date="2026-03-31",
            body="Estoy muy insatisfecho con el servicio",
        )

        assert email.id == "123"
        assert email.thread_id == "thread_456"
        assert email.sender == "cliente@example.com"
        assert email.subject == "Problema con servicio"
        assert email.date == "2026-03-31"
        assert email.body == "Estoy muy insatisfecho con el servicio"

    def test_email_is_frozen(self):
        """Email debe ser inmutable (frozen)"""
        email = Email(
            id="123",
            thread_id="thread_456",
            sender="cliente@example.com",
            subject="Problema",
            date="2026-03-31",
            body="Contenido",
        )

        with pytest.raises(AttributeError):
            email.id = "456"

    def test_email_empty_body(self):
        """Email debe permitir body vacío"""
        email = Email(
            id="123",
            thread_id="thread_456",
            sender="cliente@example.com",
            subject="",
            date="2026-03-31",
            body="",
        )

        assert email.body == ""
        assert email.subject == ""


class TestSentimentResult:
    """Tests para la entidad SentimentResult"""

    def test_sentiment_result_creation_descontento(self):
        """Debe crear un SentimentResult para descontento"""
        result = SentimentResult(
            sentimiento="descontento",
            score=0.95,
            evidencia="Cita exacta del cliente",
        )

        assert result.sentimiento == "descontento"
        assert result.score == 0.95
        assert result.evidencia == "Cita exacta del cliente"

    def test_sentiment_result_creation_neutral(self):
        """Debe crear un SentimentResult para neutral"""
        result = SentimentResult(
            sentimiento="neutral",
            score=0.50,
            evidencia="Sin evidencia clara",
        )

        assert result.sentimiento == "neutral"
        assert result.score == 0.50

    def test_sentiment_result_creation_contento(self):
        """Debe crear un SentimentResult para contento"""
        result = SentimentResult(
            sentimiento="contento",
            score=0.92,
            evidencia="Feliz con la solución",
        )

        assert result.sentimiento == "contento"
        assert result.score == 0.92

    def test_sentiment_result_is_frozen(self):
        """SentimentResult debe ser inmutable"""
        result = SentimentResult(
            sentimiento="descontento",
            score=0.95,
            evidencia="Evidencia",
        )

        with pytest.raises(AttributeError):
            result.sentimiento = "contento"

    def test_sentiment_result_valid_scores(self):
        """Score debe estar entre 0 y 1"""
        for score in [0.0, 0.25, 0.5, 0.75, 1.0]:
            result = SentimentResult(
                sentimiento="neutral",
                score=score,
                evidencia="Test",
            )
            assert 0.0 <= result.score <= 1.0
