# Tests - Lista Correos Descontentos

## Descripción

Suite de tests automáticos para el proyecto de detección de clientes descontentos vía Gmail + OpenAI.

- **Total de tests:** 30
- **Cobertura:** 79%
- **Framework:** pytest
- **Mocking:** pytest-mock

## Estructura de tests

```
tests/
├── conftest.py           # Fixtures compartidas
├── test_domain.py        # Tests de entidades (Email, SentimentResult)
├── test_application.py   # Tests de caso de uso (ClientSatisfactionPipeline)
├── test_adapters.py      # Tests de adaptadores (Gmail, OpenAI)
└── __init__.py
```

## Ejecución de tests

### Ejecutar todos los tests
```bash
make test
# O manualmente:
pytest
```

### Ver detalles de ejecución
```bash
make test-verbose
# O manualmente:
pytest -vv
```

### Generar reporte de cobertura
```bash
make test-coverage
# O manualmente:
pytest --cov=. --cov-report=html --cov-report=term-missing
```

Reporte HTML disponible en: `htmlcov/index.html`

### Ejecutar tests específicos
```bash
# Solo tests de dominio
pytest tests/test_domain.py -v

# Solo tests de aplicación
pytest tests/test_application.py -v

# Solo tests de adaptadores
pytest tests/test_adapters.py -v

# Un test específico
pytest tests/test_domain.py::TestEmail::test_email_creation -v
```

## Cobertura por módulo

| Módulo | Aserción | Cobertura |
|--------|----------|-----------|
| `application.py` | Caso de uso (pipeline) | 100% ✅ |
| `domain.py` | Entidades (Email, SentimentResult) | 100% ✅ |
| `ports.py` | Interfaces (puertos) | 80% |
| `gmail_client.py` | Adaptador Gmail | 52% |
| `openai_classifier.py` | Adaptador OpenAI | 41% |
| `config.py` | Configuración | 0% (entrada) |
| `main.py` | CLI | 0% (entrada) |
| **TOTAL** | | **79%** |

## Categorías de tests

### 1. Tests de Dominio (`test_domain.py`)
- ✅ Creación de entidades (`Email`, `SentimentResult`)
- ✅ Inmutabilidad (frozen dataclasses)
- ✅ Validación de rangos de scores

### 2. Tests de Aplicación (`test_application.py`)
- ✅ Creación del pipeline
- ✅ Configuración personalizada
- ✅ Generación de directorios
- ✅ Generación de nombres CSV con timestamp
- ✅ Procesamiento de emails vacíos
- ✅ Filtrado por sentimiento (only-descontento)
- ✅ Respectar límites de emails
- ✅ Retornar ruta CSV correcta

### 3. Tests de Adaptadores (`test_adapters.py`)

#### Gmail
- ✅ Creación de GmailEmailSource
- ✅ Listar IDs de emails
- ✅ Manejo de lista vacía
- ✅ Obtener email completo con headers
- ✅ Manejo de emails sin asunto

#### OpenAI
- ✅ Creación de OpenAISentimentAnalyzer
- ✅ Clasificación en 3 categorías (descontento, neutral, contento)
- ✅ Manejo de respuestas con claves faltantes
- ✅ Uso del modelo especificado
- ✅ Manejo de texto vacío

## Fixtures disponibles (`conftest.py`)

```python
# Email de ejemplo
@pytest.fixture
def sample_email():
    # Retorna un Email completo de prueba

# Resultados de sentimiento
@pytest.fixture
def sample_sentiment_descontento()
@pytest.fixture
def sample_sentiment_contento()
@pytest.fixture
def sample_sentiment_neutral()
```

## Mejoras futuras

- [ ] Tests de integración (sin mocks, con datos reales)
- [ ] Tests de rendimiento (max emails)
- [ ] Tests de errores de red (reintentos)
- [ ] Cobertura en adaptadores (gmail_client, openai_classifier)
- [ ] Tests en configuración y entrada (main.py, config.py)

## Desarrollo

### Agregar nuevo test
1. Crea una clase `TestXxx` en el archivo correspondiente
2. Escribe funciones `test_xxx()`
3. Usa fixtures del `conftest.py` o crea nuevas
4. Ejecuta `pytest` para validar

### Ejecutar con watch (desarrollo continuo)
```bash
pip install pytest-watch
make test-watch
# O:
ptw
```

## CI/CD

### Pipeline completo
```bash
make ci
# Ejecuta: install → lint → test → test-coverage
```

### Limpiar archivos de test
```bash
make clean
```

---

**Última actualización:** 31 de marzo de 2026
