# Detector de correos de clientes descontentos

Este proyecto lee correos de Gmail (Google Workspace), analiza el texto con OpenAI y genera un fichero CSV con el resultado.

## Requisitos

1. Python 3.10+
2. `pip install -r requirements.txt`
3. Preparar credenciales de Gmail API:
   - Crear proyecto en Google Cloud Console.
   - Habilitar Gmail API.
   - Descarga `credentials.json` y colócala en la raíz del proyecto.

4. Copiar `.env.example` a `.env` y configurar tus variables.

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

### Salida

El resultado se genera en:
- `output/clients_<YYYYMMDD_HHMMSS>.csv`

Ejemplo: `output/clients_20260331_143501.csv`

## Estructura del CSV

- `fecha_email`
- `remitente`
- `asunto`
- `sentimiento`
- `score`
- `evidencia`
- `id_email`
- `thread_id`

## Nota

Este proyecto usa el endpoint de OpenAI para classification mediante prompt (cuidado con datos sensibles, revisar tu acuerdo de privacidad).
