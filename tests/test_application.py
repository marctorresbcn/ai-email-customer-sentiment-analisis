import os
import tempfile
import csv
import pytest
from unittest.mock import Mock, MagicMock

from domain import Email, SentimentResult
from ports import EmailSource, SentimentAnalyzer
from application import ClientSatisfactionPipeline


@pytest.fixture
def mock_email_source():
    """Mock de EmailSource para tests"""
    source = Mock(spec=EmailSource)
    return source


@pytest.fixture
def mock_sentiment_analyzer():
    """Mock de SentimentAnalyzer para tests"""
    analyzer = Mock(spec=SentimentAnalyzer)
    return analyzer


@pytest.fixture
def temp_output_dir():
    """Crea un directorio temporal para archivos CSV"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestClientSatisfactionPipeline:
    """Tests para ClientSatisfactionPipeline (caso de uso)"""

    def test_pipeline_creation(self, mock_email_source, mock_sentiment_analyzer):
        """Debe crear pipeline correctamente"""
        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
        )

        assert pipeline.email_source is mock_email_source
        assert pipeline.sentiment_analyzer is mock_sentiment_analyzer
        assert pipeline.output_dir == "output"
        assert pipeline.csv_prefix == "clients"

    def test_pipeline_custom_config(self, mock_email_source, mock_sentiment_analyzer):
        """Debe crear pipeline con configuración personalizada"""
        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
            output_dir="custom_output",
            csv_prefix="custom_prefix",
        )

        assert pipeline.output_dir == "custom_output"
        assert pipeline.csv_prefix == "custom_prefix"

    def test_ensure_output_dir_creates_directory(
        self, mock_email_source, mock_sentiment_analyzer, temp_output_dir
    ):
        """Debe crear directorio de salida si no existe"""
        new_dir = os.path.join(temp_output_dir, "new_output")
        assert not os.path.exists(new_dir)

        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
            output_dir=new_dir,
        )
        pipeline._ensure_output_dir()

        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)

    def test_generate_csv_path_format(
        self, mock_email_source, mock_sentiment_analyzer, temp_output_dir
    ):
        """Debe generar ruta CSV con formato YYYYMMDD_HHMMSS"""
        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
            output_dir=temp_output_dir,
            csv_prefix="test_prefix",
        )

        csv_path = pipeline._generate_csv_path()

        # Verificar formato: test_prefix_YYYYMMDD_HHMMSS.csv
        basename = os.path.basename(csv_path)
        assert basename.startswith("test_prefix_")
        assert basename.endswith(".csv")
        assert len(basename) == len("test_prefix_YYYYMMDD_HHMMSS.csv")

    def test_run_with_empty_emails(
        self, mock_email_source, mock_sentiment_analyzer, temp_output_dir
    ):
        """Pipeline debe manejar lista vacía de emails"""
        mock_email_source.list_email_ids.return_value = []

        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
            output_dir=temp_output_dir,
        )

        csv_path = pipeline.run(max_emails=10)

        assert os.path.exists(csv_path)
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 0

    def test_run_with_single_email_descontento(
        self, mock_email_source, mock_sentiment_analyzer, temp_output_dir, capsys
    ):
        """Pipeline debe procesar email descontento correctamente"""
        email = Email(
            id="email_123",
            thread_id="thread_456",
            sender="cliente@example.com",
            subject="Problema con servicio",
            date="2026-03-31",
            body="Estoy muy insatisfecho con el servicio",
        )

        sentiment = SentimentResult(
            sentimiento="descontento",
            score=0.95,
            evidencia="muy insatisfecho",
        )

        mock_email_source.list_email_ids.return_value = ["email_123"]
        mock_email_source.fetch_email.return_value = email
        mock_sentiment_analyzer.analyze.return_value = sentiment

        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
            output_dir=temp_output_dir,
        )

        csv_path = pipeline.run(max_emails=10)

        assert os.path.exists(csv_path)
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["sentimiento"] == "descontento"
            assert rows[0]["remitente"] == "cliente@example.com"
            assert rows[0]["score"] == "0.95"
            assert rows[0]["evidencia"] == "muy insatisfecho"

        captured = capsys.readouterr()
        assert "Problema con servicio" in captured.out
        assert "descontento" in captured.out

    def test_run_only_descontento_filter(
        self, mock_email_source, mock_sentiment_analyzer, temp_output_dir
    ):
        """Pipeline debe filtrar solo emails descontento con flag"""
        emails = [
            Email(
                id="email_1",
                thread_id="thread_1",
                sender="cliente1@example.com",
                subject="Descontento",
                date="2026-03-31",
                body="Muy insatisfecho",
            ),
            Email(
                id="email_2",
                thread_id="thread_2",
                sender="cliente2@example.com",
                subject="Neutral",
                date="2026-03-31",
                body="Contenido neutral",
            ),
            Email(
                id="email_3",
                thread_id="thread_3",
                sender="cliente3@example.com",
                subject="Contento",
                date="2026-03-31",
                body="Muy contento",
            ),
        ]

        sentiments = [
            SentimentResult("descontento", 0.95, "insatisfecho"),
            SentimentResult("neutral", 0.50, "neutral"),
            SentimentResult("contento", 0.92, "contento"),
        ]

        mock_email_source.list_email_ids.return_value = ["email_1", "email_2", "email_3"]
        mock_email_source.fetch_email.side_effect = emails
        mock_sentiment_analyzer.analyze.side_effect = sentiments

        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
            output_dir=temp_output_dir,
        )

        csv_path = pipeline.run(max_emails=10, only_descontento=True)

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["sentimiento"] == "descontento"
            assert rows[0]["remitente"] == "cliente1@example.com"

    def test_run_skips_empty_body_emails(
        self, mock_email_source, mock_sentiment_analyzer, temp_output_dir
    ):
        """Pipeline debe saltar emails con body vacío"""
        emails = [
            Email(
                id="email_1",
                thread_id="thread_1",
                sender="cliente1@example.com",
                subject="Con contenido",
                date="2026-03-31",
                body="Contenido válido",
            ),
            Email(
                id="email_2",
                thread_id="thread_2",
                sender="cliente2@example.com",
                subject="Vacío",
                date="2026-03-31",
                body="   ",  # Solo espacios
            ),
        ]

        sentiments = [
            SentimentResult("descontento", 0.95, "insatisfecho"),
            SentimentResult("neutral", 0.50, "neutral"),  # No debería analizarse
        ]

        mock_email_source.list_email_ids.return_value = ["email_1", "email_2"]
        mock_email_source.fetch_email.side_effect = emails
        mock_sentiment_analyzer.analyze.return_value = sentiments[0]

        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
            output_dir=temp_output_dir,
        )

        csv_path = pipeline.run(max_emails=10)

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            # El analyzer solo debería haber sido llamado una vez
            mock_sentiment_analyzer.analyze.assert_called_once()

    def test_run_respects_max_emails(
        self, mock_email_source, mock_sentiment_analyzer, temp_output_dir
    ):
        """Pipeline debe respetar límite de emails"""
        mock_email_source.list_email_ids.return_value = ["email_1", "email_2", "email_3"]

        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
            output_dir=temp_output_dir,
        )

        pipeline.run(max_emails=5)

        # Verificar que se pasó max_results=5 al source
        mock_email_source.list_email_ids.assert_called_once_with(max_results=5)

    def test_run_returns_csv_path(
        self, mock_email_source, mock_sentiment_analyzer, temp_output_dir
    ):
        """Pipeline debe retornar ruta del CSV generado"""
        mock_email_source.list_email_ids.return_value = []

        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
            output_dir=temp_output_dir,
        )

        csv_path = pipeline.run(max_emails=10)

        assert isinstance(csv_path, str)
        assert csv_path.endswith(".csv")
        assert os.path.exists(csv_path)
