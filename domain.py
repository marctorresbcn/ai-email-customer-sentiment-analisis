from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    id: str
    thread_id: str
    sender: str
    subject: str
    date: str
    body: str


@dataclass(frozen=True)
class SentimentResult:
    sentimiento: str
    score: float
    evidencia: str
