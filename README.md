# 📧 Analizador de Sentimiento de Emails de Clientes

Herramienta para detectar clientes descontentos automáticamente leyendo emails de Gmail y analizándolos con OpenAI.

**Uso perfecto para:** e-commerce, customer support, análisis de reclamaciones, detección de problemas de servicio.

---

## ⚡ Quick Start (5 minutos)

### 1. Instalación

```bash
# Clonar y entrar
git clone https://github.com/marctorresbcn/ai-email-customer-sentiment-analisis.git
cd ai-email-customer-sentiment-analisis

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
nano .env  # o abre con tu editor favorito
```

**Rellenar solo 2 campos (obligatorios):**
- `OPENAI_API_KEY` → Obtén en https://platform.openai.com/api-keys
- `GMAIL_CREDENTIALS_FILE` → Descarga `credentials.json` desde Google Cloud Console

### 3. Ejecutar

```bash
python main.py --max-emails 50
```

**Salida:** `output/clients_YYYYMMDD_HHMMSS.csv`

---

## 📚 Ejemplos de uso (de simple a complejo)

### Ejemplo 1: Procesar últimas 100 mails

```bash
python main.py
```

### Ejemplo 2: Último mes, solo clientes descontentos

```bash
python main.py --preset-range last_month --only-descontento
```

### Ejemplo 3: Tienda barefoot - filtrar por categoría

Procesa solo correos sobre: pedidos, devoluciones, tallas, cambios, problemas de envío.

```bash
python main.py \
  --keywords "pedidos,devoluciones,tallas,cambios,returns,exchange,problema envío" \
  --preset-range last_month \
  --max-emails 300
```

### Ejemplo 4: Búsqueda a alias de soporte específico

```bash
python main.py \
  --to support@empresa.com \
  --from-date 2026-01-01 \
  --max-emails 500 \
  --only-descontento \
  --min-score 0.75
```

### Ejemplo 5: Obtener TODOS los emails históricos

```bash
python main.py --from-date 2000-01-01 --max-emails 50000
```

---

## 🔧 Referencia de parámetros CLI

| Flag | Tipo | Descripción | Ejemplo |
|------|------|-------------|---------|
| `--max-emails` | Número | Máximo emails a procesar (default: 100) | `--max-emails 500` |
| `--from-date` | Fecha | Desde esta fecha hasta ahora (YYYY-MM-DD) | `--from-date 2026-01-01` |
| `--date-range` | 2 Fechas | Rango específico (YYYY-MM-DD YYYY-MM-DD) | `--date-range 2026-03-01 2026-03-31` |
| `--preset-range` | Opción | Rango predefinido | `--preset-range last_month` |
| `--to` | Email | Correos dirigidos a este alias | `--to support@empresa.com` |
| `--keywords` | Texto | Palabras clave en asunto (separadas por comas) | `--keywords pedidos,returns,tallas` |
| `--only-descontento` | Flag | Solo exportar clientes descontentos | (sin argumento) |
| `--min-score` | Número | Score mínimo para "descontento" (0.0-1.0) | `--min-score 0.75` |
| `--exclude-domains` | Texto | Dominios a excluir (separados por comas) | `--exclude-domains google.com,shopify.com` |
| `--dry-run` | Flag | Preview de emails sin llamar a OpenAI (sin coste) | (sin argumento) |

**Notas:**
- Los rangos de **fecha son excluyentes** entre sí: usa solo uno (`--from-date` O `--date-range` O `--preset-range`)
- Los demás parámetros pueden combinarse libremente
- CLI sobrescribe valores del `.env`
- `--dry-run` es ideal para validar filtros antes de un run real

---

## ⚙️ Variables de configuración (.env)

### Mínimas requeridas

| Variable | Descripción |
|----------|-------------|
| `OPENAI_API_KEY` | API key de OpenAI (https://platform.openai.com/api-keys) |
| `GMAIL_CREDENTIALS_FILE` | Ruta a `credentials.json` (Google Cloud Console) |

### Recomendadas

| Variable | Descripción | Default |
|----------|-------------|---------|
| `OPENAI_MODEL` | Modelo OpenAI a usar | `gpt-4o-mini` |
| `MAX_EMAILS` | Máximo emails por ejecución | `100` |
| `MIN_SCORE_DESCONTENTO` | Score mínimo para marcar como "descontento" (0.0-1.0) | `0.60` |
| `KEYWORDS_FILTER` | Palabras clave para filtrar asuntos (comas separadas) | (vacío) |
| `EXCLUDE_DOMAINS` | Dominios de remitente a excluir antes de llamar a OpenAI (ahorra coste) | (vacío) |
| `GMAIL_LABELS` | Carpetas a buscar (comas separadas). Dejar vacío para buscar en todos los correos incluyendo archivados | `INBOX` |
| `CSV_PREFIX` | Prefijo del archivo de salida | `clients` |

### Avanzadas

| Variable | Descripción | Default |
|----------|-------------|---------|
| `GMAIL_TOKEN_FILE` | Archivo para guardar token OAuth | `token.json` |
| `GMAIL_USER_ID` | ID del usuario Gmail | `me` |
| `GMAIL_QUERY` | Query nativa de Gmail | (vacío) |
| `OUTPUT_DIR` | Directorio de salida | `output` |
| `LOG_LEVEL` | Nivel de logs | `INFO` |

### Ejemplo .env completo

```env
# Obligatorio
OPENAI_API_KEY=sk-proj-your-key-here
GMAIL_CREDENTIALS_FILE=credentials.json

# Opcional (recomendado rellenar)
OPENAI_MODEL=gpt-4o-mini
MAX_EMAILS=100
MIN_SCORE_DESCONTENTO=0.60
KEYWORDS_FILTER=pedidos,devoluciones,tallas,returns,exchange
EXCLUDE_DOMAINS=google.com,shopify.com,klaviyo.com
GMAIL_LABELS=INBOX  # dejar vacío para incluir correos archivados

# Output
OUTPUT_DIR=output
CSV_PREFIX=clients
LOG_LEVEL=INFO
```

---

## 📊 Estructura del CSV de salida

**Ejemplo de archivo generado:** `output/clients_20260331_143501.csv`

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `fecha_email` | Fecha del correo (ISO format) | `2026-03-31T14:35:00Z` |
| `remitente` | Email del remitente | `cliente@tienda.com` |
| `asunto` | Subject del correo | `Mi pedido no llegó a tiempo` |
| `sentimiento` | Clasificación | `descontento` / `neutral` / `contento` |
| `score` | Confianza del análisis (0.0-1.0) | `0.92` |
| `evidencia` | Fragmento que justifica la clasificación | `"No me llegó a tiempo y me decepcionó"` |
| `id_email` | ID único de Gmail | `18a3c5d234f5e1a2` |
| `thread_id` | ID del hilo de conversación | `abc123def456` |

---

## 📌 Casos de uso típicos

### Tienda online: Encontrar reclamaciones sobre envíos

```bash
python main.py --keywords "envío,retraso,no llegó,dañado,perdido" \
               --preset-range last_week \
               --only-descontento
```

### SaaS: Feedback de usuarios frustrados

```bash
python main.py --to support@empresa.com \
               --preset-range last_month \
               --only-descontento \
               --min-score 0.80
```

### E-commerce: Análisis mensual completo

```bash
python main.py --preset-range last_month \
               --max-emails 1000 \
               --keywords "pedidos,devoluciones,tallas,calidad"
```

### Auditoría: Todos los correos del año pasado

```bash
python main.py --from-date 2025-01-01 \
               --max-emails 50000
```

---

## 🎯 Entender el "Score" de descontento

El **score** es un número de **0.0 a 1.0** que indica la confianza del análisis:

- **0.0 - 0.33**: Débil (poco probable que sea ese sentimiento)
- **0.33 - 0.66**: Moderado (podría ser ese sentimiento)
- **0.66 - 1.0**: Fuerte (altamente probable que sea ese sentimiento)

¿Por qué `MIN_SCORE_DESCONTENTO=0.60` por defecto?
- Capta descontentos claros pero no los ambiguos
- Reduce falsos positivos
- Puedes ajustar:
  - **Más estricto** (menos ruido): `--min-score 0.80`
  - **Más permisivo** (más cobertura): `--min-score 0.50`

---

## ⚠️ Consideraciones importantes

### Privacidad y seguridad

El contenido de los emails se envía a OpenAI para análisis.

- Revisa políticas de privacidad de OpenAI
- Consulta con team legal si usas datos sensibles
- Considera anonimizar información antes de procesar

### Costos

- **OpenAI**: ~$0.00001 por token. Con 1000 emails: ~$0.50-$2 (depende del modelo)
- **Google Gmail API**: 1M requests/día (gratis)
- Usa `gpt-4o-mini` para máxima economía

### Rendimiento

- 100 emails: ~2 minutos
- 1000 emails: ~20 minutos
- 10000 emails: ~3-4 horas (según modelo)

---

## 🛠️ Desarrollo y Testing

```bash
# Instalar con dependencias de test
pip install -r requirements.txt

# Ejecutar tests
make test

# Ver cobertura
make test-coverage

# Lint del código
make lint
```

---

## 📖 Requisitos técnicos

- Python 3.10+
- Google Workspace con Gmail API habilitada
- Cuenta OpenAI con API keys

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. El proyecto sigue arquitectura hexagonal y SOLID principles.

---

## 📄 Licencia

Ver [LICENSE](LICENSE)
