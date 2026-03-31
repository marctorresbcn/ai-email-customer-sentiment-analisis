import pytest
from unittest.mock import Mock, patch, MagicMock
from domain import Email, SentimentResult
from gmail_client import GmailEmailSource
from openai_classifier import OpenAISentimentAnalyzer


class TestGmailEmailSource:
    """Tests para el adaptador GmailEmailSource"""

    @patch("gmail_client.get_service")
    def test_gmail_email_source_creation(self, mock_get_service):
        """Debe crear GmailEmailSource correctamente"""
        mock_service = Mock()
        mock_get_service.return_value = mock_service

        source = GmailEmailSource(
            credentials_path="test_creds.json",
            token_path="test_token.pickle",
        )

        assert source.credentials_path == "test_creds.json"
        assert source.token_path == "test_token.pickle"

    @patch("gmail_client.get_service")
    def test_list_email_ids(self, mock_get_service):
        """Debe retornar lista de IDs de email"""
        mock_service = Mock()
        mock_service.users().messages().list().execute.return_value = {
            "messages": [
                {"id": "msg_1"},
                {"id": "msg_2"},
                {"id": "msg_3"},
            ]
        }
        mock_get_service.return_value = mock_service

        source = GmailEmailSource(
            credentials_path="test_creds.json",
            token_path="test_token.pickle",
        )

        email_ids = source.list_email_ids(max_results=10)

        assert len(email_ids) == 3
        assert "msg_1" in email_ids
        assert "msg_2" in email_ids
        assert "msg_3" in email_ids

    @patch("gmail_client.get_service")
    def test_list_email_ids_empty(self, mock_get_service):
        """Debe retornar lista vacía si no hay emails"""
        mock_service = Mock()
        mock_service.users().messages().list().execute.return_value = {}
        mock_get_service.return_value = mock_service

        source = GmailEmailSource(
            credentials_path="test_creds.json",
            token_path="test_token.pickle",
        )

        email_ids = source.list_email_ids(max_results=10)

        assert email_ids == []

    @patch("gmail_client.get_service")
    @patch("gmail_client.extract_message_body")
    def test_fetch_email(self, mock_extract_body, mock_get_service):
        """Debe traer email con todos los campos"""
        mock_service = Mock()
        mock_message = {
            "id": "msg_123",
            "threadId": "thread_456",
            "payload": {
                "headers": [
                    {"name": "From", "value": "cliente@example.com"},
                    {"name": "Subject", "value": "Consulta importante"},
                    {"name": "Date", "value": "2026-03-31T10:00:00Z"},
                ]
            },
        }
        mock_service.users().messages().get().execute.return_value = mock_message
        mock_extract_body.return_value = "Body content here"
        mock_get_service.return_value = mock_service

        source = GmailEmailSource(
            credentials_path="test_creds.json",
            token_path="test_token.pickle",
        )

        email = source.fetch_email("msg_123")

        assert isinstance(email, Email)
        assert email.id == "msg_123"
        assert email.thread_id == "thread_456"
        assert email.sender == "cliente@example.com"
        assert email.subject == "Consulta importante"
        assert email.body == "Body content here"

    @patch("gmail_client.get_service")
    def test_fetch_email_missing_subject(self, mock_get_service):
        """Debe manejar emails sin asunto"""
        mock_service = Mock()
        mock_message = {
            "id": "msg_123",
            "threadId": "thread_456",
            "payload": {
                "headers": [
                    {"name": "From", "value": "cliente@example.com"},
                    {"name": "Date", "value": "2026-03-31T10:00:00Z"},
                ]
            },
        }
        mock_service.users().messages().get().execute.return_value = mock_message

        with patch("gmail_client.extract_message_body", return_value="Body"):
            mock_get_service.return_value = mock_service

            source = GmailEmailSource(
                credentials_path="test_creds.json",
                token_path="test_token.pickle",
            )

            email = source.fetch_email("msg_123")

            assert email.subject == ""


class TestOpenAISentimentAnalyzer:
    """Tests para el adaptador OpenAISentimentAnalyzer"""

    @patch("openai_classifier.setup_openai")
    def test_sentiment_analyzer_creation(self, mock_setup):
        """Debe crear OpenAISentimentAnalyzer correctamente"""
        analyzer = OpenAISentimentAnalyzer(api_key="test_key")

        assert analyzer.model == "gpt-4o-mini"
        assert analyzer.max_tokens == 250
        assert analyzer.temperature == 0.0
        mock_setup.assert_called_once_with("test_key")

    @patch("openai_classifier.classify_sentiment")
    @patch("openai_classifier.setup_openai")
    def test_analyze_sentiment_descontento(self, mock_setup, mock_classify):
        """Debe clasificar email descontento correctamente"""
        mock_classify.return_value = {
            "sentimiento": "descontento",
            "score": 0.95,
            "evidencia": "muy insatisfecho con el servicio",
        }

        analyzer = OpenAISentimentAnalyzer(api_key="test_key")
        result = analyzer.analyze("Estoy muy insatisfecho con el servicio")

        assert isinstance(result, SentimentResult)
        assert result.sentimiento == "descontento"
        assert result.score == 0.95
        assert result.evidencia == "muy insatisfecho con el servicio"

    @patch("openai_classifier.classify_sentiment")
    @patch("openai_classifier.setup_openai")
    def test_analyze_sentiment_contento(self, mock_setup, mock_classify):
        """Debe clasificar email contento correctamente"""
        mock_classify.return_value = {
            "sentimiento": "contento",
            "score": 0.92,
            "evidencia": "muy satisfecho",
        }

        analyzer = OpenAISentimentAnalyzer(api_key="test_key")
        result = analyzer.analyze("Estoy muy satisfecho con el servicio")

        assert result.sentimiento == "contento"
        assert result.score == 0.92

    @patch("openai_classifier.classify_sentiment")
    @patch("openai_classifier.setup_openai")
    def test_analyze_sentiment_neutral(self, mock_setup, mock_classify):
        """Debe clasificar email neutral correctamente"""
        mock_classify.return_value = {
            "sentimiento": "neutral",
            "score": 0.50,
            "evidencia": "sin indicador claro",
        }

        analyzer = OpenAISentimentAnalyzer(api_key="test_key")
        result = analyzer.analyze("Aquí está tu información")

        assert result.sentimiento == "neutral"
        assert result.score == 0.50

    @patch("openai_classifier.classify_sentiment")
    @patch("openai_classifier.setup_openai")
    def test_analyze_with_missing_keys(self, mock_setup, mock_classify):
        """Debe manejar respuesta con claves faltantes"""
        mock_classify.return_value = {
            "sentimiento": "neutral",
            # Score y evidencia faltan
        }

        analyzer = OpenAISentimentAnalyzer(api_key="test_key")
        result = analyzer.analyze("texto de prueba")

        assert result.sentimiento == "neutral"
        assert result.score == 0.5  # Valor por defecto
        assert result.evidencia == ""  # Valor por defecto

    @patch("openai_classifier.classify_sentiment")
    @patch("openai_classifier.setup_openai")
    def test_analyze_uses_correct_model(self, mock_setup, mock_classify):
        """Debe usar el modelo especificado"""
        mock_classify.return_value = {
            "sentimiento": "neutral",
            "score": 0.50,
            "evidencia": "test",
        }

        analyzer = OpenAISentimentAnalyzer(
            api_key="test_key",
            model="gpt-4-turbo",
        )
        analyzer.analyze("test")

        # Verificar que se pasó el modelo correcto
        mock_classify.assert_called_once_with("test", model="gpt-4-turbo")

    @patch("openai_classifier.classify_sentiment")
    @patch("openai_classifier.setup_openai")
    def test_analyze_with_empty_text(self, mock_setup, mock_classify):
        """Debe manejar texto vacío"""
        mock_classify.return_value = {
            "sentimiento": "neutral",
            "score": 0.0,
            "evidencia": "texto vacío",
        }

        analyzer = OpenAISentimentAnalyzer(api_key="test_key")
        result = analyzer.analyze("")

        assert result.sentimiento == "neutral"
