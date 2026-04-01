# 📧 Analizador de Sentimiento de Emails de Clientes

Herramienta para detectar clientes descontentos automáticamente leyendo emails de Gmail y analizándolos con OpenAI.

**Uso perfecto para:** e-commerce, customer support, análisis de reclamaciones, detección de problemas de servicio.

---

## 📑 Índice de contenidos

1. [⚡ Quick Start (5 minutos)](#-quick-start-5-minutos)
2. [📚 Ejemplos de uso](#-ejemplos-de-uso-de-simple-a-complejo)
3. [🔧 Referencia de parámetros CLI](#-referencia-de-parámetros-cli)
4. [⚙️ Configuración .env](#%EF%B8%8F-variables-de-configuración-env)
5. [📊 Estructura del CSV](#-estructura-del-csv-de-salida)
6. [📈 Análisis avanzado con consolidador](#-análisis-avanzado-consolidador-multi-vista)
7. [🎯 Entender el Score](#-entender-el-score-de-descontento)
8. [⚠️ Consideraciones importantes](#%EF%B8%8F-consideraciones-importantes)

---

## 🎬 ¿Cómo funciona? (2 minutos)

```
Gmail (tus emails)
      ↓
Filtras por fechas, palabras clave, remitente, etc.
      ↓
OpenAI analiza sentimiento de cada email
      ↓
📊 Se generan automáticamente 2 reportes:

   CSV                          Excel (3 pestañas)
   ├── Emails planos            ├── Todos los emails (datos crudos)
   └── Datos crudos             ├── Análisis por cliente (⭐ la más importante)
                                └── Casos críticos (qué hacer primero)
      ↓
💡 Identificas clientes insatisfechos + acciones correctivas
```

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

### 3. Tu primer análisis

```bash
python main.py --max-emails 50
```

**Salida automática:**
```
output/2026-04-01_143501/
├── clients_20260401_143501.csv          (emails procesados)
└── consolidado_evolucion.xlsx           (análisis automático 📊)
```

✅ **¡Listo!** Tu primer análisis está completo con reportes automáticos.

---

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

## 📈 Análisis avanzado: Consolidador multi-vista

Tras procesar emails, el sistema genera automáticamente un **Excel con 3 pestañas** que agrupa datos por cliente, identifica tendencias y detecta casos críticos.

### 🚀 Cómo funciona (paso a paso)

```
1. Ejecutas análisis normal
   ↓
2. Se crea carpeta: output/2026-04-01_143501/
   ↓
3. Se guardan CSV(s) con emails procesados
   ↓
4. ✅ AUTOMÁTICAMENTE se genera consolidado_evolucion.xlsx
   ↓
5. Tu navegador/Excel se abre con 3 pestañas listas
```

### 📁 Estructura de carpetas (nueva)

**Antes (viejo):** Todo en `output/` sin orden
```
output/
├── clients_20260401_104030.csv
├── clients_20260401_104031.csv
├── clients_20260328_143501.csv
└── consolidado_evolucion.csv
```

**Ahora (nuevo):** Carpetas por ejecución timestamped ✨
```
output/
├── 2026-04-01_143501/         ← Ejecución 1 (fecha_hora)
│   ├── clients_*.csv          (tus emails procesados)
│   └── consolidado_evolucion.xlsx  (análisis automático)
│
├── 2026-03-28_092030/         ← Ejecución 2
│   ├── clients_*.csv
│   └── consolidado_evolucion.xlsx
│
└── 2026-03-15_143501/         ← Ejecución 3
    ├── clients_*.csv
    └── consolidado_evolucion.xlsx
```

**Ventajas:**
- ✅ Historial completo de cada run (nada se pierde)
- ✅ Cada carpeta es independiente y auditrable
- ✅ Fácil comparar tendencias entre períodos
- ✅ Sin riesgo de sobrescribir datos

### 📊 Las 3 pestañas del Excel (explicadas)

#### 📋 Pestaña 1: "Todos los emails"

Simple y plana: todos tus emails con sus detalles básicos.

| Columna | Qué es | Ejemplo |
|---------|--------|---------|
| `remitente` | Email de quién escribió | `maria@gmail.com` |
| `asunto` | Asunto del correo | `Mi pedido no llegó` |
| `score` | Confianza del análisis (0.0-1.0) | `0.85` |
| `sentimiento` | Clasificación | `descontento` / `neutral` / `contento` |
| `evidencia` | Frase clave que lo justifica | `"Lleva 5 días y sin llegar"` |
| `fecha_email` | Cuándo se escribió | `2026-03-25 14:30` |

**Úsala para:** Búsquedas rápidas, filtros personalizados, ver detalles específicos.

#### 📊 Pestaña 2: "Análisis por cliente" ← **LA MÁS IMPORTANTE**

Agrupa todo por cliente + alertas automáticas. Aquí es donde ves patrones.

| Columna | Qué es | Ejemplo | Por qué importa |
|---------|--------|---------|-----------------|
| `remitente` | Email del cliente | `maria@gmail.com` | Identificar quién |
| `num_contactos` | Cuántas veces escribió | `5` | 5 emails = cliente recurrente |
| `score_promedio` | Promedio de insatisfacción | `0.64` | Su satisfacción general |
| `num_descontento` | Contactos explícitamente descontento | `2` | Descontento confirmado |
| `primer_contacto` | Cuándo escribió por primera vez | `2026-02-10` | Duración del problema |
| `ultimo_contacto` | Su email más reciente | `2026-03-25` | ¿Qué tan fresca la queja? |
| `temas` | Resumen de asuntos | `Retraso envío \| Error...` | Causa del problema |
| `tendencia` | ¿Mejora o empeora? | `📈 (empeora)` | ¿Va bien tu acción correctiva? |
| `alerta` | 🚨 Banderas automáticas | `⚠️ Múltiples descontentos` | **Acción a tomar** |
| `recomendacion` | Qué hacer | `Revisión prioritaria` | Tu siguiente paso |

**Banderas automáticas (`alerta`):**
- `🚨 ESCALADA DETECTADA` ← **Máxima urgencia** → Score subió abruptamente + múltiples contactos
- `⚠️ Múltiples descontentos` ← **Alto riesgo** → 2+ emails con descontento
- `📍 Cliente recurrente insatisfecho` ← **Problema persistente** → 3+ contactos con promedio alto de insatisfacción
- `⛔ Mínimo de satisfacción bajo` ← **Nunca contento** → Incluso su mejor contacto tiene score alto (≥0.7)
- `✓` ← **Sin alertas** → Está bien, monitorear

**Recomendaciones automáticas (`recomendacion`):**
- `CONTACTO URGENTE` ← Escalada detectada (actúa hoy) 🔴
- `Revisión prioritaria` ← Múltiples descontentos (actúa esta semana) 🟠
- `Seguimiento` ← Problema persistente (implementar mejoras) 🟡
- `Monitorear` ← Sin alertas (mantener vigilancia) 🟢

#### 🚨 Pestaña 3: "Casos críticos"

Solo los clientes que NECESITAN atención especial. Es un resumen ejecutivo.

| Criterio | Qué significa | Ejemplo |
|----------|---------------|---------|
| `Múltiples descontentos` | Cliente escribió 2+ veces con descontento | "Maria escribió insatisfecha dos veces" |
| `Escalada abrupta` | Score saltó de bajo a alto | "Juan pasó de 0.2 a 0.9 (empeoramiento brusco)" |
| `Insatisfacción persistente` | Contactos numerosos + promedio alto | "Pedro contactó 4 veces con promedio 0.75" |

**Esta pestaña responde:** ¿A quiénes debo llamar hoy?

### 🎓 Ejemplo práctico: Interpretando un cliente

**Tu Excel muestra:**
```
remitente:         maria@gmail.com
num_contactos:     5
score_promedio:    0.64
num_descontento:   2
primer_contacto:   2026-02-10
ultimo_contacto:   2026-03-25
temas:             Retraso envío | Calidad baja | Cambio de talla
tendencia:         📈 (empeora)
alerta:            ⚠️ Múltiples descontentos | 📍 Cliente recurrente insatisfecho
recomendacion:     Revisión prioritaria
```

**Interpretación:**
- Maria ha contactado 5 veces durante ~6 semanas
- 2 de esos contactos fueron explícitamente descontento
- Su satisfacción promedio es moderada-baja (0.64 / 1.0)
- **Lo importante:** Está empeorando (última es más insatisfecha que la primera)
- Problema recurrente (múltiples temas: envío, calidad, talla)

**Acción recomendada:**
1. ✅ Llama a Maria hoy (está escalando)
2. ✅ Investiga: ¿cuál es el problema de fondo? (¿logística? ¿calidad? ¿comunicación?)
3. ✅ Ofrece solución concreta (descuento, regalo, devolución)
4. **Meta:** En próximo run, su score debe bajar

### 💡 Tips para usar los datos

**1. Priorizar clientes (por audacia):**
```excel
En "Análisis por cliente", ordena por:
score_promedio DESC  ← Los más insatisfechos arriba
```
Así ves a quiénes te enfocas primero.

**2. Encontrar problemas sistémicos:**
```excel
Filtra por alerta = "🚨" u "⚠️"
Analiza la columna "temas"
Si 3+ clientes reclaman "envío lento" → PROBLEMA LOGÍSTICO
```

**3. Ver si tus acciones funcionan:**
```excel
Compara dos ejecuciones (ej: mayo vs junio)
Mira la columna "tendencia" 
Si ves ↑ "📉 (mejora)" → ¡Tus cambios funcionan!
Si ves ↓ "📈 (empeora)" → Necesitas otro enfoque
```

**4. Validar antes de escalar:**
```excel
Cliente con alerta "🚨" pero:
- score_promedio = 0.25 (bajo)
¿Qué pasó? → Recién escaló pero antes estaba contento
→ Problema nuevo y urgente
```

### 🔧 Generar reporte manualmente

Normalmente se genera automáticamente, pero si necesitas re-analizar una carpeta anterior:

```bash
# Analizar una ejecución específica
python consolidate_analysis.py output/2026-03-15_143501/

# O sin parámetros = la más reciente
python consolidate_analysis.py
```

### 📈 Flujo típico (meses)

**Semana 1:** 
```bash
python main.py --date-range 2026-03-01 2026-04-01
→ output/2026-04-01_HHMMSS/consolidado_evolucion.xlsx
→ Identificas clientes críticos
```

**Semana 2-3:** Implementas acciones correctivas

**Semana 4:**
```bash
python main.py --date-range 2026-04-01 2026-05-01
→ output/2026-05-01_HHMMSS/consolidado_evolucion.xlsx
→ Comparas tendencias: ¿Mejoraron mis acciones?
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

## 🚀 Guía rápida: "Qué hacer con los datos"

Una vez tienes el Excel, ¿cuál es el siguiente paso? Aquí va:

### Mañana (urgente - 30 minutos)
```
1. Abre "Casos críticos"
2. ¿Alguien con alerta "🚨"?
   → Llama a ese cliente HOY
   
3. ¿Alguien con score promedio > 0.8?
   → Envía email de disculpas + oferta especial
```

### Esta semana (importante - 2-3 horas)
```
1. Abre "Análisis por cliente"
2. Ordena por score_promedio DESC
3. Para cada cliente en top 10:
   a. Lee sus "temas"
   b. Identifica patrón (¿envío? ¿calidad? ¿comunicación?)
   c. Documenta acción correctiva
   
Ejemplo:
- 3 clientes reclaman "envío lento" 
  → Problema logístico, contactar proveedor de envíos
```

### Próximo mes (mejora)
```
1. Ejecuta análisis del siguiente período
2. Compara columna "tendencia"
   - ¿Ves más "📉 (mejora)"?
   - Tu acción correctiva funcionó ✅
   - ¿Ves más "📈 (empeora)"?
   - Necesitas otro enfoque ❌
```

### Dashboard personal (opcional)
```
Haz un Google Sheet con:
- Clientes críticos + acciones pendientes
- Problemas sistémicos detectados
- Resultados de acciones (antes/después)
- Tendencias generales por mes
```

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
