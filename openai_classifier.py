import json
from openai import OpenAI
from domain import SentimentResult


class OpenAISentimentAnalyzer:
    def __init__(self, api_key: str, model: str, max_tokens: int = 250, temperature: float = 0.0):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.client = OpenAI(api_key=api_key)

    def analyze(self, text: str) -> SentimentResult:
        result = classify_sentiment(self.client, text, model=self.model)
        return SentimentResult(
            sentimiento=result.get("sentimiento", "neutral"),
            score=result.get("score", 0.5),
            evidencia=result.get("evidencia", ""),
        )


def classify_sentiment(client: OpenAI, text: str, model: str = "gpt-4o-mini") -> dict:
    prompt = (
        "Eres un analista de satisfacción de clientes. "
        "Analiza el correo completo para determinar si el cliente expresa descontento, frustración o insatisfacción. "
        "Considera el tono general, expresiones de enojo, quejas específicas, no solo menciones de demoras, devoluciones, reembolsos, returns o preguntas informativas sobre pedidos. "
        "Quejas técnicas simples sobre la web/app (como enlaces rotos o problemas de acceso) sin expresiones de frustración intensa deben clasificarse como neutral con score bajo. "
        "Preguntas simples sobre el estado del pedido, devoluciones, reembolsos o returns sin expresiones negativas deben clasificarse como neutral con score bajo. "
        "Responde estrictamente en formato JSON con las claves:\n"
        "- sentimiento: \"descontento\" o \"neutral\" o \"contento\"\n"
        "- score: número entre 0.0 y 1.0, donde 1.0 es máximo descontento (frustración intensa) y 0.0 es máxima satisfacción\n"
        "- evidencia: fragmento de texto que justifique la clasificación, enfocándote en expresiones de sentimiento\n"
        "\nCorreo:\n" + text + "\n\nRespuesta JSON:\n"
    )

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Eres un clasificador de sentimiento de clientes."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=250,
    )

    raw = resp.choices[0].message.content.strip()

    # Eliminar markdown code fences si el modelo las incluye
    if raw.startswith("```"):
        raw = raw.split("```")[-2] if raw.count("```") >= 2 else raw
        raw = raw.lstrip("json").strip()

    # Intentar parsear JSON
    try:
        parsed = json.loads(raw)
    except Exception:
        # Si no es JSON válido, tratar como texto libre.
        parsed = {
            "sentimiento": "neutral",
            "score": 0.5,
            "evidencia": raw.replace("\n", " ").strip()[:512],
        }

    # Normalizar sentimiento
    sentimiento = str(parsed.get("sentimiento", "neutral")).lower()
    if sentimiento not in ["descontento", "neutral", "contento"]:
        if any(w in sentimiento for w in ["negat", "malo", "queja", "insatis", "no "]):
            sentimiento = "descontento"
        elif any(w in sentimiento for w in ["posit", "bien", "satisf", "feliz", "contento"]):
            sentimiento = "contento"
        else:
            sentimiento = "neutral"

    try:
        score = float(parsed.get("score", 0.5))
    except Exception:
        score = 0.5

    evidencia = str(parsed.get("evidencia", "")).strip()

    return {
        "sentimiento": sentimiento,
        "score": min(max(score, 0.0), 1.0),
        "evidencia": evidencia,
    }
