from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable

from domain import Email, SentimentResult


class EmailSource(ABC):
    @abstractmethod
    def list_email_ids(self, max_results: int) -> list[str]:
        pass

    @abstractmethod
    def fetch_email(self, email_id: str) -> Email:
        pass


class SentimentAnalyzer(ABC):
    @abstractmethod
    def analyze(self, text: str) -> SentimentResult:
        pass
