# Detector de correos de clientes descontentos

Este proyecto lee correos de Gmail (Google Workspace), analiza el texto con OpenAI y genera un fichero CSV con el resultado.

## 📋 Índice de contenidos

1. [Requisitos](#requisitos)
2. [Configuración de variables (.env)](#configuración-de-variables-env)
3. [Uso](#uso)
4. [Obtener TODOS los correos de la cuenta](#obtener-todos-los-correos-de-la-cuenta)
5. [Estructura del CSV](#estructura-del-csv)
6. [Notas de privacidad](#notas-de-privacidad)

---

## Requisitos

1. Python 3.10+
2. `pip install -r requirements.txt`
3. Preparar credenciales de Gmail API:
   - Crear proyecto en Google Cloud Console.
   - Habilitar Gmail API.
   - Descarga `credentials.json` y colócala en la raíz del proyecto.

4. Copiar `.env.example` a `.env` y configurar tus variables.

## Configuración de variables (.env)

Después de copiar `.env.example` a `.env`, edita los valores según tu entorno. Aquí está la descripción completa de cada variable:

### OpenAI Configuration

| Variable | Obligatoria | Descripción | Ejemplo |
|----------|-----------|-------------|---------|
| `OPENAI_API_KEY` | ✅ Sí | API key de OpenAI para clasificación de sentimiento. Obtén en https://platform.openai.com/api-keys | `sk-proj-xxxxx...` |
| `OPENAI_MODEL` | ⚠️ Opcional | Modelo de OpenAI a utilizar para la clasificación de sentimiento. Modelos disponibles: `gpt-4o`, `gpt-4-turbo`, `gpt-4o-mini` (default, más económico), `gpt-3.5-turbo` (rápido pero menos preciso) | `gpt-4o-mini` |

### Gmail Configuration

| Variable | Obligatoria | Descripción | Ejemplo |
|----------|-----------|-------------|---------|
| `GMAIL_CREDENTIALS_FILE` | ✅ Sí | Ruta al archivo `credentials.json` descargado de Google Cloud Console | `credentials.json` |
| `GMAIL_TOKEN_FILE` | ⚠️ Opcional | Nombre del archivo donde se guarda el token de autorización (se crea automáticamente en primer uso) | `token.json` |
| `GMAIL_USER_ID` | ⚠️ Opcional | ID del usuario (casi siempre `me` para tu propia cuenta) | `me` |
| `GMAIL_LABELS` | ⚠️ Opcional | Etiquetas/carpetas de Gmail a buscar, separadas por comas. `INBOX` es la carpeta predeterminada | `INBOX` o `INBOX,SENT,ARCHIVE` |
| `GMAIL_QUERY` | ⚠️ Opcional | Consulta adicional de Gmail (sintaxis nativa de Gmail). Se combina con los filtros CLI | `filename:pdf` o vacío |

### Processing Configuration

| Variable | Obligatoria | Descripción | Ejemplo |
|----------|-----------|-------------|---------|
| `MAX_EMAILS` | ⚠️ Opcional | Número máximo de correos a procesar por defecto. Puede ser sobrescrito con `--max-emails` CLI | `100` |
| `MIN_SCORE_DESCONTENTO` | ⚠️ Opcional | Score mínimo (0.0 a 1.0) para considerar un email como "descontento". Valores cercanos a 1.0 son más estrictos | `0.60` |

### Output Configuration

| Variable | Obligatoria | Descripción | Ejemplo |
|----------|-----------|-------------|---------|
| `OUTPUT_DIR` | ⚠️ Opcional | Directorio donde se guardan los CSV generados | `output` |
| `CSV_PREFIX` | ⚠️ Opcional | Prefijo del archivo CSV de salida. El nombre final será `{CSV_PREFIX}_YYYYMMDD_HHMMSS.csv` | `clients` |

### Logging Configuration

| Variable | Obligatoria | Descripción | Ejemplo |
|----------|-----------|-------------|---------|
| `LOG_LEVEL` | ⚠️ Opcional | Nivel de logs a mostrar: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `INFO` |

### Ejemplo de .env completo

```env
# OpenAI
OPENAI_API_KEY=sk-proj-your-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Gmail
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_USER_ID=me
GMAIL_LABELS=INBOX
GMAIL_QUERY=

# Processing
MAX_EMAILS=100
MIN_SCORE_DESCONTENTO=0.60

# Output
OUTPUT_DIR=output
CSV_PREFIX=clients

# Logging
LOG_LEVEL=INFO
```

---

## Uso

```bash
python main.py --max-emails 50
```

### Opciones de límite de emails

- `--max-emails`: número máximo de correos a procesar (por defecto `100`).

### Filtros de fecha

Puedes usar uno de los siguientes filtros (mutuamente excluyentes):

- `--from-date YYYY-MM-DD`: desde esa fecha hasta ahora.
  ```bash
  python main.py --from-date 2026-03-01
  ```

- `--date-range YYYY-MM-DD YYYY-MM-DD`: rango específico de fechas.
  ```bash
  python main.py --date-range 2026-03-01 2026-03-31
  ```

- `--preset-range {last_week|last_month|last_three_months|last_year}`: rango predefinido.
  ```bash
  python main.py --preset-range last_month
  ```

### Filtro de destinatario

- `--to email@domain.com`: correos dirigidos a un email específico (útil para alias corporativos).
  ```bash
  python main.py --to support@empresa.com
  ```

### Filtro de sentimiento

- `--only-descontento`: exporta solo correos clasificados como descontento.
  ```bash
  python main.py --max-emails 100 --only-descontento
  ```

### Ejemplos combionados

```bash
# Último mes, solo a alias de soporte, máximo 200 emails
python main.py --preset-range last_month --to support@empresa.com --max-emails 200

# Rango específico, solo descontentos
python main.py --date-range 2026-03-01 2026-03-31 --only-descontento

# Desde una fecha específica a un destinatario
python main.py --from-date 2026-01-01 --to sales@empresa.com
```

### Combinación de filtros

Los filtros se pueden combinar de la siguiente manera:

| Combinación | Ejemplo | Estado |
|-------------|---------|--------|
| **Fecha + Destinatario** | `--preset-range last_month --to support@empresa.com` | ✅ Permitido |
| **Fecha + Máximo emails** | `--from-date 2026-01-01 --max-emails 100` | ✅ Permitido |
| **Fecha + Solo descontentos** | `--date-range 2026-03-01 2026-03-31 --only-descontento` | ✅ Permitido |
| **Destinatario + Máximo** | `--to sales@empresa.com --max-emails 50` | ✅ Permitido |
| **Múltiples flags** | `--preset-range last_week --to alias@empresa.com --max-emails 200 --only-descontento` | ✅ Permitido |

**Nota:** Los filtros de fecha son mutuamente excluyentes (solo uno a la vez). No se pueden combinar `--from-date`, `--date-range` y `--preset-range` entre sí.

---

## Obtener TODOS los correos de la cuenta

Si deseas procesar **todos los correos** de tu buzón (sin filtros específicos), tienes dos opciones:

### Opción 1: Sin filtros CLI (recomendado para empezar)

```bash
python main.py --max-emails 500
```

Esto obtendrá **hasta 500 correos de la carpeta INBOX** (valor por defecto).

### Opción 2: Búsqueda desde el inicio del tiempo

Para obtener **prácticamente todos los correos históricos**, usa una fecha muy antigua:

```bash
python main.py --from-date 2000-01-01 --max-emails 10000
```

Esto obtiene todos los correos desde el año 2000 hasta ahora, limitados a 10.000 (puedes aumentar el límite según necesites).

### Opción 3: Cambiar etiquetas/carpetas en `.env`

Si quieres incluir **múltiples carpetas** (INBOX, SENT, ARCHIVE, etc.), modifica tu archivo `.env`:

```env
GMAIL_LABELS=INBOX,SENT,ARCHIVE,ALL_MAIL
MAX_EMAILS=10000
```

Luego ejecuta:

```bash
python main.py
```

Esto procesará todos los correos de las carpetas especificadas.

### Opción 4: Usar GMAIL_QUERY para búsquedas avanzadas

Para una búsqueda más precisa, puedes agregar una `GMAIL_QUERY` en tu `.env`:

```env
# Buscar todos excepto spam/basura
GMAIL_QUERY=is:unspam -is:chat

# Buscar desde una fecha específica
GMAIL_QUERY=after:2025-01-01

# Buscar correos con adjuntos
GMAIL_QUERY=has:attachment
```

La sintaxis completa de búsqueda de Gmail está disponible en: https://support.google.com/mail/answer/7190

### ⚠️ Consideraciones importantes

- **Cuota de API**: Google limita a 1 millón de emails/día aproximadamente. Para búsquedas masivas, distribuye en varias ejecuciones.
- **Costo de OpenAI**: Cada email clasificado consume tokens. Con 10.000 emails y un modelo como `gpt-4o-mini`, el costo estimado es bajo, pero ten presente que cada token tiene un costo.
- **Tiempo de ejecución**: Procesar 10.000+ emails puede tomar horas dependiendo de la proxies y el modelo OpenAI.

### Salida

El resultado se genera en:
- `output/clients_<YYYYMMDD_HHMMSS>.csv`

Ejemplo: `output/clients_20260331_143501.csv`

## Estructura del CSV

- `fecha_email`: Fecha del correo en formato ISO
- `remitente`: Dirección de email del remitente
- `asunto`: Asunto del correo
- `sentimiento`: Clasificación (`descontento`, `neutral`, `contento`)
- `score`: Puntuación de confianza (0.0 a 1.0)
- `evidencia`: Fragmento del texto o razón de la clasificación
- `id_email`: ID único de Gmail
- `thread_id`: ID del hilo de conversación

---

## Notas de privacidad

⚠️ Este proyecto usa el endpoint de OpenAI para clasificación mediante prompt. **Esto significa que el contenido de los correos se envía a los servidores de OpenAI**.

Antes de usar este proyecto con datos sensibles o corporativos:
1. **Revisa tu acuerdo de privacidad** con OpenAI
2. **Consulta con tu equipo legal/compliance** sobre el tratamiento de datos
3. **Considera usar el modelo `gpt-4o-mini`** (más económico y rápido)
4. **Revisa las políticas de retención** de OpenAI (por defecto, los datos se retienen y pueden usarse para entrenar)
5. **Anonimiza datos sensibles** si es posible antes de procesar
