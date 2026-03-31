.PHONY: help install test test-verbose test-coverage test-unit test-integration lint format clean

help:
	@echo "Comandos disponibles:"
	@echo "  make install           - Instala dependencias"
	@echo "  make test              - Ejecuta todos los tests"
	@echo "  make test-verbose      - Executa tests con verbosidad alta"
	@echo "  make test-coverage     - Ejecuta tests y genera reporte de coverage"
	@echo "  make test-unit         - Ejecuta solo tests unitarios"
	@echo "  make lint              - Verifica sintaxis Python"
	@echo "  make format            - Formatea código (si está disponible)"
	@echo "  make clean             - Limpia archivos temporales"

install:
	pip install -r requirements.txt

test:
	pytest

test-verbose:
	pytest -vv

test-coverage:
	pytest --cov=. --cov-report=html --cov-report=term-missing
	@echo "Reporte de coverage generado en htmlcov/index.html"

test-unit:
	pytest -m unit

test-watch:
	pytest-watch

lint:
	python -m py_compile config.py gmail_client.py openai_classifier.py application.py main.py domain.py ports.py
	@echo "✓ Sintaxis validada"

format:
	black . --line-length 100 || echo "black no instalado"
	isort . || echo "isort no instalado"

clean:
	rm -rf .pytest_cache __pycache__ tests/__pycache__
	rm -rf .coverage htmlcov
	rm -rf *.pyc
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

ci: install lint test test-coverage
	@echo "✓ CI pipeline completado exitosamente"
