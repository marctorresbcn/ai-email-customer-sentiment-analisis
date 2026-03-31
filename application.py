import csv
import os
from datetime import datetime

from domain import Email, SentimentResult
from ports import EmailSource, SentimentAnalyzer


class ClientSatisfactionPipeline:
    def __init__(self, email_source: EmailSource, sentiment_analyzer: SentimentAnalyzer, output_dir: str = "output", csv_prefix: str = "clients", min_score_descontento: float = 0.60):
        self.email_source = email_source
        self.sentiment_analyzer = sentiment_analyzer
        self.output_dir = output_dir
        self.csv_prefix = csv_prefix
        self.min_score_descontento = min_score_descontento

    def _ensure_output_dir(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)

    def _generate_csv_path(self) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.csv_prefix}_{ts}.csv"
        return os.path.join(self.output_dir, filename)

    def run(self, max_emails: int, only_descontento: bool = False) -> str:
        email_ids = self.email_source.list_email_ids(max_results=max_emails)

        self._ensure_output_dir()
        csv_path = self._generate_csv_path()

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "fecha_email",
                    "remitente",
                    "asunto",
                    "sentimiento",
                    "score",
                    "evidencia",
                    "id_email",
                    "thread_id",
                ],
            )
            writer.writeheader()

            for idx, email_id in enumerate(email_ids, start=1):
                email = self.email_source.fetch_email(email_id)
                if not email.body.strip():
                    continue

                sentiment_result = self.sentiment_analyzer.analyze(email.body)

                if only_descontento:
                    if sentiment_result.sentimiento != "descontento" or sentiment_result.score < self.min_score_descontento:
                        continue

                writer.writerow(
                    {
                        "fecha_email": email.date,
                        "remitente": email.sender,
                        "asunto": email.subject,
                        "sentimiento": sentiment_result.sentimiento,
                        "score": sentiment_result.score,
                        "evidencia": sentiment_result.evidencia,
                        "id_email": email.id,
                        "thread_id": email.thread_id,
                    }
                )

                print(f"[{idx}/{len(email_ids)}] {email.subject or '<sin asunto>'} -> {sentiment_result.sentimiento} ({sentiment_result.score})")

        print(f"CSV generado: {csv_path}")
        return csv_path
