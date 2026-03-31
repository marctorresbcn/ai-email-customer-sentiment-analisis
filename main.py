import argparse

from application import ClientSatisfactionPipeline
from config import load_settings
from gmail_client import GmailEmailSource
from openai_classifier import OpenAISentimentAnalyzer
from query_builder import GmailQueryBuilder


def main() -> None:
    parser = argparse.ArgumentParser(description="Detector de clientes descontentos")
    parser.add_argument("--max-emails", type=int, help="Número máximo de emails", default=None)
    parser.add_argument(
        "--only-descontento", action="store_true", help="Solo exportar correos con sentimiento descontento"
    )
    
    # Filtros de fecha
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        "--from-date",
        type=str,
        help="Desde una fecha hasta ahora (formato: YYYY-MM-DD)",
        default=None,
    )
    date_group.add_argument(
        "--date-range",
        type=str,
        nargs=2,
        metavar=("FROM", "TO"),
        help="Rango de fechas (formato: YYYY-MM-DD YYYY-MM-DD)",
        default=None,
    )
    date_group.add_argument(
        "--preset-range",
        type=str,
        choices=["last_week", "last_month", "last_three_months", "last_year"],
        help="Rango predefinido",
        default=None,
    )
    
    # Filtro de destinatario
    parser.add_argument(
        "--to",
        type=str,
        help="Correos dirigidos a un email específico (ej: alias@empresa.com)",
        default=None,
    )
    
    # Filtro de palabras clave
    parser.add_argument(
        "--keywords",
        type=str,
        help="Palabras clave separadas por comas para filtrar (ej: 'pedidos,devoluciones,tallas')",
        default=None,
    )
    
    args = parser.parse_args()

    settings = load_settings()
    if args.max_emails:
        settings.max_emails = args.max_emails

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY no está configurado en .env")

    # Construir query con filtros
    query_builder = GmailQueryBuilder(base_query=settings.gmail_query)
    
    if args.from_date:
        query_builder.add_from_date(args.from_date)
    
    if args.date_range:
        query_builder.add_date_range(args.date_range[0], args.date_range[1])
    
    if args.preset_range:
        query_builder.add_preset_range(args.preset_range)
    
    if args.to:
        query_builder.add_recipient(args.to)
    
    # Procesar palabras clave desde CLI o .env
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
        if keywords:
            query_builder.add_keywords(keywords)
    elif settings.keywords_filter:
        query_builder.add_keywords(settings.keywords_filter)
    
    final_query = query_builder.build()

    email_source = GmailEmailSource(
        credentials_path=settings.gmail_credentials_file,
        token_path=settings.gmail_token_file,
        user_id=settings.gmail_user_id,
        labels=settings.gmail_labels,
        query=final_query,
    )

    sentiment_analyzer = OpenAISentimentAnalyzer(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )

    pipeline = ClientSatisfactionPipeline(
        email_source=email_source,
        sentiment_analyzer=sentiment_analyzer,
        output_dir=settings.output_dir,
        csv_prefix=settings.csv_prefix,
    )

    pipeline.run(max_emails=settings.max_emails, only_descontento=args.only_descontento)


if __name__ == "__main__":
    main()
