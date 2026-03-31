import pytest
import sys
from pathlib import Path

# Agregamos el directorio raíz al path para que los imports funcionen
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))


@pytest.fixture
def sample_email():
    """Fixture: Email de ejemplo para tests"""
    from domain import Email

    return Email(
        id="test_email_123",
        thread_id="test_thread_456",
        sender="cliente@example.com",
        subject="Consulta de servicio",
        date="2026-03-31T10:00:00Z",
        body="Tengo una consulta sobre el servicio",
    )


@pytest.fixture
def sample_sentiment_descontento():
    """Fixture: Resultado de sentimiento descontento"""
    from domain import SentimentResult

    return SentimentResult(
        sentimiento="descontento",
        score=0.88,
        evidencia="Cliente menciona insatisfacción repeated",
    )


@pytest.fixture
def sample_sentiment_contento():
    """Fixture: Resultado de sentimiento contento"""
    from domain import SentimentResult

    return SentimentResult(
        sentimiento="contento",
        score=0.90,
        evidencia="Cliente agradece la solución",
    )


@pytest.fixture
def sample_sentiment_neutral():
    """Fixture: Resultado de sentimiento neutral"""
    from domain import SentimentResult

    return SentimentResult(
        sentimiento="neutral",
        score=0.50,
        evidencia="Sin indicadores de sentimiento claro",
    )
