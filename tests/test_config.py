"""Tests para config.py"""

import os
from unittest.mock import patch

import pytest

from config import Settings, load_settings


class TestSettings:
    """Test suite para la clase Settings."""

    def test_settings_dataclass_fields(self):
        """Test: verificar que Settings tenga todos los campos."""
        settings = Settings(
            openai_api_key="test-key",
            openai_model="gpt-4o-mini",
            gmail_credentials_file="credentials.json",
            gmail_token_file="token.json",
            gmail_user_id="me",
            gmail_labels=["INBOX"],
            gmail_query="",
            keywords_filter=[],
            max_emails=100,
            output_dir="output",
            csv_prefix="clients",
            min_score_descontento=0.60,
            log_level="INFO",
        )
        assert settings.openai_api_key == "test-key"
        assert settings.keywords_filter == []

    def test_keywords_filter_empty_list(self):
        """Test: keywords_filter vacío por defecto."""
        settings = Settings(
            openai_api_key="test-key",
            openai_model="gpt-4o-mini",
            gmail_credentials_file="credentials.json",
            gmail_token_file="token.json",
            gmail_user_id="me",
            gmail_labels=["INBOX"],
            gmail_query="",
            keywords_filter=[],
            max_emails=100,
            output_dir="output",
            csv_prefix="clients",
            min_score_descontento=0.60,
            log_level="INFO",
        )
        assert settings.keywords_filter == []


class TestLoadSettings:
    """Test suite para load_settings()."""

    @patch.dict(os.environ, {}, clear=True)
    def test_load_settings_defaults(self):
        """Test: cargar configuración con valores por defecto."""
        settings = load_settings()
        assert settings.openai_model == "gpt-4o-mini"
        assert settings.gmail_credentials_file == "credentials.json"
        assert settings.gmail_token_file == "token.json"
        assert settings.gmail_user_id == "me"
        assert settings.gmail_labels == ["INBOX"]
        assert settings.keywords_filter == []
        assert settings.max_emails == 100
        assert settings.csv_prefix == "clients"

    @patch.dict(os.environ, {"KEYWORDS_FILTER": "pedidos,devoluciones,tallas"})
    def test_load_settings_keywords_filter(self):
        """Test: cargar keywords_filter desde .env."""
        settings = load_settings()
        assert settings.keywords_filter == ["pedidos", "devoluciones", "tallas"]

    @patch.dict(os.environ, {"KEYWORDS_FILTER": "  PEDIDOS  ,  DEVOLUCIONES  "})
    def test_load_settings_keywords_filter_normalization(self):
        """Test: keywords_filter se normalizan a minúsculas y se limpian espacios."""
        settings = load_settings()
        assert settings.keywords_filter == ["pedidos", "devoluciones"]

    @patch.dict(os.environ, {"KEYWORDS_FILTER": ""})
    def test_load_settings_keywords_filter_empty_string(self):
        """Test: KEYWORDS_FILTER vacío devuelve lista vacía."""
        settings = load_settings()
        assert settings.keywords_filter == []

    @patch.dict(os.environ, {"KEYWORDS_FILTER": ",,,,"})
    def test_load_settings_keywords_filter_only_commas(self):
        """Test: KEYWORDS_FILTER solo con comas devuelve lista vacía."""
        settings = load_settings()
        assert settings.keywords_filter == []

    @patch.dict(os.environ, {"OPENAI_MODEL": "gpt-4-turbo"})
    def test_load_settings_custom_model(self):
        """Test: cargar modelo personalizado."""
        settings = load_settings()
        assert settings.openai_model == "gpt-4-turbo"

    @patch.dict(os.environ, {"MAX_EMAILS": "500"})
    def test_load_settings_custom_max_emails(self):
        """Test: cargar max_emails personalizado."""
        settings = load_settings()
        assert settings.max_emails == 500

    @patch.dict(os.environ, {"GMAIL_LABELS": "INBOX,SUPPORT,BILLING"})
    def test_load_settings_multiple_labels(self):
        """Test: cargar múltiples etiquetas de Gmail."""
        settings = load_settings()
        assert settings.gmail_labels == ["INBOX", "SUPPORT", "BILLING"]
