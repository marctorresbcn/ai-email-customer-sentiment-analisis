import os
import openai
from domain import SentimentResult


class OpenAISentimentAnalyzer:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", max_tokens: int = 250, temperature: float = 0.0):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        setup_openai(api_key)

    def analyze(self, text: str) -> SentimentResult:
        result = classify_sentiment(text, model=self.model)
        return SentimentResult(
            sentimiento=result.get("sentimiento", "neutral"),
            score=result.get("score", 0.5),
            evidencia=result.get("evidencia", ""),
        )


def setup_openai(api_key: str):
    openai.api_key = api_key


def classify_sentiment(text: str, model: str = "gpt-4o-mini") -> dict:
    prompt = (
        "Eres un analista de satisfacción de clientes. "
        "En base al correo que sigue, responde estrictamente en formato JSON con las claves:\n"
        "- sentimiento: \"descontento\" o \"neutral\" o \"contento\"\n"
        "- score: número entre 0.0 y 1.0\n"
        "- evidencia: fragmento de texto que indique descontento (o explicative para neutral/contento)\n"
        "\nCorreo:\n" + text + "\n\nRespuesta JSON:\n"
    )

    resp = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "Eres un clasificador de sentimiento de clientes."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=250,
    )

    raw = resp["choices"][0]["message"]["content"].strip()

    # Intentar parsear JSON
    import json

    try:
        parsed = json.loads(raw)
    except Exception:
        # Si no es JSON válido, tratar como texto libre.
        parsed = {
            "sentimiento": "neutral",
            "score": 0.5,
            "evidencia": raw.replace("\n", " ").strip()[:512],
        }

    # Normalizar
    sentimiento = str(parsed.get("sentimiento", "neutral")).lower()
    if sentimiento not in ["descontento", "neutral", "contento"]:
        if "no" in sentimiento or "malo" in sentimiento or "queja" in sentimiento or "insatis" in sentimiento:
            sentimiento = "descontento"
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
