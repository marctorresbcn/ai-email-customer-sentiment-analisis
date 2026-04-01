import os
import tempfile
import csv
import json
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

    @staticmethod
    def _get_generated_export_paths(execution_folder: str) -> tuple[str, str]:
        generated_files = os.listdir(execution_folder)
        csv_files = [f for f in generated_files if f.endswith(".csv")]
        json_files = [f for f in generated_files if f.endswith(".json")]

        assert len(csv_files) == 1
        assert len(json_files) == 1

        return (
            os.path.join(execution_folder, csv_files[0]),
            os.path.join(execution_folder, json_files[0]),
        )

    @staticmethod
    def _read_export_rows(execution_folder: str) -> tuple[list[dict[str, str]], list[dict[str, str | float]]]:
        csv_path, json_path = TestClientSatisfactionPipeline._get_generated_export_paths(execution_folder)

        with open(csv_path, "r", encoding="utf-8") as f:
            csv_rows = list(csv.DictReader(f))

        with open(json_path, "r", encoding="utf-8") as f:
            json_rows = json.load(f)

        return csv_rows, json_rows

    def test_pipeline_creation(self, mock_email_source, mock_sentiment_analyzer):
        """Debe crear pipeline correctamente"""
        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
        )

        assert pipeline.email_source is mock_email_source
        assert pipeline.sentiment_analyzer is mock_sentiment_analyzer
        assert pipeline.base_output_dir == "output"
        assert pipeline.output_dir.startswith("output/")
        assert pipeline.csv_prefix == "clients"
        assert pipeline.min_score_descontento == 0.60

    def test_dry_run_with_emails(self, mock_email_source, mock_sentiment_analyzer, capsys):
        """Test que dry_run muestra preview sin procesar con IA."""
        mock_emails = [
            Email(
                id="1",
                thread_id="t1",
                date="2026-03-25",
                sender="cliente1@test.com",
                subject="Mi pedido",
                body="El envío tardó mucho"
            ),
            Email(
                id="2",
                thread_id="t2",
                date="2026-03-24",
                sender="cliente2@test.com",
                subject="Duda talla",
                body="¿Qué talla me recomiendas?"
            ),
        ]
        mock_email_source.list_email_ids.return_value = ["1", "2"]
        mock_email_source.fetch_email.side_effect = mock_emails

        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer
        )

        # dry_run no debe lanzar excepción
        pipeline.dry_run(max_emails=100)

        # Verifica que se llamó a list_email_ids pero NO a sentiment_analyzer
        mock_email_source.list_email_ids.assert_called_once_with(max_results=100)
        mock_sentiment_analyzer.analyze.assert_not_called()  # ← NO llama a OpenAI
        
        # Verifica que se mostró el preview en consola
        captured = capsys.readouterr()
        assert "DRY-RUN MODE" in captured.out
        assert "Total emails encontrados: 2" in captured.out

    def test_dry_run_no_emails(self, mock_email_source, mock_sentiment_analyzer, capsys):
        """Test que dry_run maneja caso de sin emails."""
        mock_email_source.list_email_ids.return_value = []

        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer
        )

        # dry_run no debe lanzar excepción
        pipeline.dry_run(max_emails=100)

        mock_sentiment_analyzer.analyze.assert_not_called()
        
        # Verifica que mostró mensaje de no encontrados
        captured = capsys.readouterr()
        assert "No se encontraron emails" in captured.out

    def test_pipeline_custom_config(self, mock_email_source, mock_sentiment_analyzer):
        """Debe crear pipeline con configuración personalizada"""
        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
            output_dir="custom_output",
            csv_prefix="custom_prefix",
            min_score_descontento=0.75,
        )

        assert pipeline.base_output_dir == "custom_output"
        assert pipeline.output_dir.startswith("custom_output/")
        assert pipeline.csv_prefix == "custom_prefix"
        assert pipeline.min_score_descontento == 0.75

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

        execution_folder = pipeline.run(max_emails=10)
        csv_path, json_path = self._get_generated_export_paths(execution_folder)
        assert os.path.exists(csv_path)
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 0

        with open(json_path, "r", encoding="utf-8") as f:
            rows = json.load(f)
            assert rows == []

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

        execution_folder = pipeline.run(max_emails=10)
        csv_path, json_path = self._get_generated_export_paths(execution_folder)
        assert os.path.exists(csv_path)
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["sentimiento"] == "descontento"
            assert rows[0]["remitente"] == "cliente@example.com"
            assert rows[0]["score"] == "0.95"
            assert rows[0]["evidencia"] == "muy insatisfecho"

        with open(json_path, "r", encoding="utf-8") as f:
            rows = json.load(f)
            assert len(rows) == 1
            assert rows[0]["sentimiento"] == "descontento"
            assert rows[0]["remitente"] == "cliente@example.com"
            assert rows[0]["score"] == 0.95
            assert rows[0]["evidencia"] == "muy insatisfecho"

        captured = capsys.readouterr()
        assert "Problema con servicio" in captured.out
        assert "descontento" in captured.out

    def test_run_with_ten_emails_generates_matching_csv_and_json(
        self, mock_email_source, mock_sentiment_analyzer, temp_output_dir
    ):
        """Pipeline debe exportar 10 emails al CSV y replicarlos en JSON."""
        email_ids = [f"email_{idx}" for idx in range(1, 11)]
        emails = [
            Email(
                id=email_id,
                thread_id=f"thread_{idx}",
                sender=f"cliente{idx}@example.com",
                subject=f"Asunto {idx}",
                date=f"2026-03-{idx:02d}T10:00:00Z",
                body=f"Cuerpo del email {idx}",
            )
            for idx, email_id in enumerate(email_ids, start=1)
        ]
        sentiments = [
            SentimentResult(
                sentimiento="descontento" if idx % 2 == 0 else "neutral",
                score=0.80 if idx % 2 == 0 else 0.55,
                evidencia=f"Evidencia {idx}",
            )
            for idx in range(1, 11)
        ]

        mock_email_source.list_email_ids.return_value = email_ids
        mock_email_source.fetch_email.side_effect = emails
        mock_sentiment_analyzer.analyze.side_effect = sentiments

        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
            output_dir=temp_output_dir,
        )

        execution_folder = pipeline.run(max_emails=10)
        csv_rows, json_rows = self._read_export_rows(execution_folder)

        assert len(csv_rows) == 10
        assert len(json_rows) == 10

        for csv_row, json_row, email, sentiment in zip(csv_rows, json_rows, emails, sentiments):
            assert csv_row["fecha_email"] == email.date == json_row["fecha_email"]
            assert csv_row["remitente"] == email.sender == json_row["remitente"]
            assert csv_row["asunto"] == email.subject == json_row["asunto"]
            assert csv_row["sentimiento"] == sentiment.sentimiento == json_row["sentimiento"]
            assert float(csv_row["score"]) == sentiment.score == json_row["score"]
            assert csv_row["evidencia"] == sentiment.evidencia == json_row["evidencia"]
            assert csv_row["id_email"] == email.id == json_row["id_email"]
            assert csv_row["thread_id"] == email.thread_id == json_row["thread_id"]

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

        execution_folder = pipeline.run(max_emails=10, only_descontento=True)
        csv_path, _ = self._get_generated_export_paths(execution_folder)

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

        execution_folder = pipeline.run(max_emails=10)
        csv_path, _ = self._get_generated_export_paths(execution_folder)

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
        mock_email_source.list_email_ids.return_value = []

        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
            output_dir=temp_output_dir,
        )

        pipeline.run(max_emails=5)

        # Verificar que se pasó max_results=5 al source
        mock_email_source.list_email_ids.assert_called_once_with(max_results=5)

    def test_run_only_descontento_with_min_score(
        self, mock_email_source, mock_sentiment_analyzer, temp_output_dir
    ):
        """Pipeline debe filtrar por score mínimo cuando --only-descontento está activo"""
        emails = [
            Email(
                id="email_1",
                thread_id="thread_1",
                sender="cliente1@example.com",
                subject="Muy descontento",
                date="2026-03-31",
                body="Muy insatisfecho",
            ),
            Email(
                id="email_2",
                thread_id="thread_2",
                sender="cliente2@example.com",
                subject="Poco descontento",
                date="2026-03-31",
                body="Algo insatisfecho",
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
            SentimentResult("descontento", 0.92, "muy insatisfecho"),  # >= 0.80, se incluye
            SentimentResult("descontento", 0.45, "algo insatisfecho"),  # < 0.80, se excluye
            SentimentResult("contento", 0.90, "contento"),  # No es descontento
        ]

        mock_email_source.list_email_ids.return_value = ["email_1", "email_2", "email_3"]
        mock_email_source.fetch_email.side_effect = emails
        mock_sentiment_analyzer.analyze.side_effect = sentiments

        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
            output_dir=temp_output_dir,
            min_score_descontento=0.80,
        )

        execution_folder = pipeline.run(max_emails=10, only_descontento=True)
        csv_path, _ = self._get_generated_export_paths(execution_folder)

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            # Solo debe incluir email_1 (descontento con score 0.92 >= 0.80)
            assert len(rows) == 1
            assert rows[0]["sentimiento"] == "descontento"
            assert rows[0]["remitente"] == "cliente1@example.com"
            assert float(rows[0]["score"]) == 0.92

    def test_run_returns_csv_path(
        self, mock_email_source, mock_sentiment_analyzer, temp_output_dir
    ):
        """Pipeline debe retornar la carpeta de ejecución con el CSV generado"""
        mock_email_source.list_email_ids.return_value = []

        pipeline = ClientSatisfactionPipeline(
            email_source=mock_email_source,
            sentiment_analyzer=mock_sentiment_analyzer,
            output_dir=temp_output_dir,
        )

        execution_folder = pipeline.run(max_emails=10)
        csv_path, _ = self._get_generated_export_paths(execution_folder)

        assert isinstance(execution_folder, str)
        assert os.path.isdir(execution_folder)
        assert os.path.exists(csv_path)
