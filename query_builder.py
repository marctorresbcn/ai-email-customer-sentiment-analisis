"""Builder para construir queries de búsqueda de Gmail."""

from datetime import datetime, timedelta
from typing import Optional


class GmailQueryBuilder:
    """Construye queries para la API de Gmail de forma segura."""

    def __init__(self, base_query: str = ""):
        """
        Inicializa el constructor.
        
        Args:
            base_query: Query base a partir de la cual construir.
        """
        self.conditions = []
        if base_query:
            self.conditions.append(base_query)

    def add_from_date(self, date_str: str) -> "GmailQueryBuilder":
        """
        Agrega condición: desde una fecha hasta ahora.
        
        Args:
            date_str: Fecha en formato YYYY-MM-DD
            
        Returns:
            self para encadenamiento.
        """
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            self.conditions.append(f'after:{date_str.replace("-", "/")}')
        except ValueError:
            raise ValueError(f"Fecha inválida: {date_str}. Usa formato YYYY-MM-DD")
        return self

    def add_date_range(self, from_date: str, to_date: str) -> "GmailQueryBuilder":
        """
        Agrega condición: rango de fechas (desde, hasta).
        
        Args:
            from_date: Fecha inicial en formato YYYY-MM-DD
            to_date: Fecha final en formato YYYY-MM-DD
            
        Returns:
            self para encadenamiento.
        """
        try:
            datetime.strptime(from_date, "%Y-%m-%d")
            datetime.strptime(to_date, "%Y-%m-%d")
            self.conditions.append(f'after:{from_date.replace("-", "/")}')
            self.conditions.append(f'before:{to_date.replace("-", "/")}')
        except ValueError:
            raise ValueError("Fechas inválidas. Usa formato YYYY-MM-DD")
        return self

    def add_preset_range(self, preset: str) -> "GmailQueryBuilder":
        """
        Agrega condición: rango predefinido.
        
        Args:
            preset: uno de [last_week, last_month, last_three_months, last_year]
            
        Returns:
            self para encadenamiento.
        """
        valid_presets = ["last_week", "last_month", "last_three_months", "last_year"]
        if preset not in valid_presets:
            raise ValueError(f"Preset inválido: {preset}. Válidos: {', '.join(valid_presets)}")

        today = datetime.now()
        if preset == "last_week":
            from_date = today - timedelta(days=7)
        elif preset == "last_month":
            from_date = today - timedelta(days=30)
        elif preset == "last_three_months":
            from_date = today - timedelta(days=90)
        else:  # last_year
            from_date = today - timedelta(days=365)

        date_str = from_date.strftime("%Y/%m/%d")
        self.conditions.append(f"after:{date_str}")
        return self

    def add_recipient(self, email: str) -> "GmailQueryBuilder":
        """
        Agrega condición: correos dirigidos a un email específico.
        
        Args:
            email: Dirección de email (ej: alias@empresa.com)
            
        Returns:
            self para encadenamiento.
        """
        if "@" not in email:
            raise ValueError(f"Email inválido: {email}")
        self.conditions.append(f"to:{email}")
        return self

    def add_sender(self, email: str) -> "GmailQueryBuilder":
        """
        Agrega condición: correos enviados desde un email específico.
        
        Args:
            email: Dirección de email del remitente
            
        Returns:
            self para encadenamiento.
        """
        if "@" not in email:
            raise ValueError(f"Email inválido: {email}")
        self.conditions.append(f"from:{email}")
        return self

    def add_keywords(self, keywords: list[str]) -> "GmailQueryBuilder":
        """
        Agrega condición: palabras clave en asunto o contenido.
        
        Args:
            keywords: Lista de palabras clave para buscar (ej: ["pedidos", "devoluciones"])
            
        Returns:
            self para encadenamiento.
        """
        if not keywords:
            return self
        
        # Normalizar: minúsculas y limpiar espacios
        normalized_keywords = [k.strip().lower() for k in keywords if k.strip()]
        if not normalized_keywords:
            return self
        
        # Construir query: OR en asunto (subject:palabra1 OR subject:palabra2)
        keyword_query = " OR ".join([f'subject:"{k}"' for k in normalized_keywords])
        self.conditions.append(f"({keyword_query})")
        return self

    def build(self) -> str:
        """
        Construye la query final.
        
        Returns:
            Query combinada con AND, o string vacío si no hay condiciones.
        """
        if not self.conditions:
            return ""
        return " ".join(self.conditions)
