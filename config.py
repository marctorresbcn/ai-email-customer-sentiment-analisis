import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    openai_api_key: str
    openai_model: str
    gmail_credentials_file: str
    gmail_token_file: str
    gmail_user_id: str
    gmail_labels: list[str]
    gmail_query: str
    keywords_filter: list[str]
    max_emails: int
    output_dir: str
    csv_prefix: str
    min_score_descontento: float
    log_level: str
    
    def validate_min_score(self) -> None:
        """Valida que min_score_descontento esté en rango válido (0.0-1.0)."""
        if not (0.0 <= self.min_score_descontento <= 1.0):
            raise ValueError(f"MIN_SCORE_DESCONTENTO debe estar entre 0.0 y 1.0, got {self.min_score_descontento}")


def load_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        gmail_credentials_file=os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json"),
        gmail_token_file=os.getenv("GMAIL_TOKEN_FILE", "token.json"),
        gmail_user_id=os.getenv("GMAIL_USER_ID", "me"),
        gmail_labels=[x.strip() for x in os.getenv("GMAIL_LABELS", "INBOX").split(",") if x.strip()],
        gmail_query=os.getenv("GMAIL_QUERY", "").strip(),
        keywords_filter=[x.strip().lower() for x in os.getenv("KEYWORDS_FILTER", "").split(",") if x.strip()],
        max_emails=int(os.getenv("MAX_EMAILS", "100")),
        output_dir=os.getenv("OUTPUT_DIR", "output"),
        csv_prefix=os.getenv("CSV_PREFIX", "clients"),
        min_score_descontento=float(os.getenv("MIN_SCORE_DESCONTENTO", "0.60")),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
