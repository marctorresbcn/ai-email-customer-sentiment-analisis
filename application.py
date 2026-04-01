import csv
import os
from datetime import datetime

from domain import Email, SentimentResult
from ports import EmailSource, SentimentAnalyzer


class ClientSatisfactionPipeline:
    def __init__(self, email_source: EmailSource, sentiment_analyzer: SentimentAnalyzer, output_dir: str = "output", csv_prefix: str = "clients", min_score_descontento: float = 0.60, exclude_domains: list[str] | None = None):
        self.email_source = email_source
        self.sentiment_analyzer = sentiment_analyzer
        self.output_dir = output_dir
        self.csv_prefix = csv_prefix
        self.min_score_descontento = min_score_descontento
        self.exclude_domains = [d.lower() for d in (exclude_domains or [])]

    def _is_excluded(self, sender: str) -> bool:
        sender_lower = sender.lower()
        return any(
            f"@{domain}" in sender_lower or f".{domain}" in sender_lower
            for domain in self.exclude_domains
        )

    def _ensure_output_dir(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)

    def _generate_csv_path(self) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.csv_prefix}_{ts}.csv"
        return os.path.join(self.output_dir, filename)

    def dry_run(self, max_emails: int) -> None:
        """Vista previa sin procesar con OpenAI (sin costo)."""
        print("\n" + "=" * 80)
        print("🔍 DRY-RUN MODE: Validación de filtros (SIN llamar a OpenAI)")
        print("=" * 80 + "\n")

        try:
            email_ids = self.email_source.list_email_ids(max_results=max_emails)
        except Exception as e:
            print(f"❌ Error al conectar con Gmail: {e}\n")
            raise

        if not email_ids:
            print("❌ No se encontraron emails con los filtros especificados.\n")
            return

        if self.exclude_domains:
            print(f"🚫 Dominios excluidos: {', '.join(self.exclude_domains)}")

        print(f"✅ Total emails encontrados: {len(email_ids)}")
        print(f"📊 Mostrando preview de los primeros 10 (tras excluir dominios):\n")
        print("-" * 80)

        shown = 0
        excluded = 0
        for email_id in email_ids:
            if shown >= 10:
                break
            try:
                email = self.email_source.fetch_email(email_id)
                if self._is_excluded(email.sender):
                    excluded += 1
                    continue
                shown += 1
                body_preview = (
                    (email.body[:120].replace("\n", " ").strip() + "...")
                    if email.body
                    else "<vacío>"
                )
                print(f"{shown}. [{email.date}]")
                print(f"   De: {email.sender}")
                print(f"   Asunto: {email.subject or '<sin asunto>'}")
                print(f"   Preview: {body_preview}")
                print()
            except Exception as e:
                print(f"❌ Error procesando email: {e}\n")

        print("-" * 80)
        if excluded:
            print(f"🚫 {excluded} emails omitidos por dominio excluido (en los primeros {shown + excluded} revisados)\n")

        print("Próximo paso: ejecuta sin --dry-run para procesar con OpenAI y generar CSV\n")
        print("=" * 80 + "\n")

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
                if self._is_excluded(email.sender):
                    print(f"[{idx}/{len(email_ids)}] Omitido (dominio excluido): {email.sender}")
                    continue
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
