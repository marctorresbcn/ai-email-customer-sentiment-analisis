"""
Consolidador de análisis de sentimiento con múltiples vistas.

Genera un archivo Excel con:
1. Datos consolidados de todos los CSVs
2. Análisis por cliente (timeline, tendencias, alertas)
3. Casos críticos para revisión manual
"""

import pandas as pd
import os
import glob
from datetime import datetime
from pathlib import Path


def load_all_csvs(folder_path: str) -> pd.DataFrame:
    """
    Carga y concatena todos los CSVs de clientes en la carpeta especificada.
    
    Args:
        folder_path: Directorio donde están los archivos CSV
        
    Returns:
        DataFrame consolidado con todos los datos
    """
    csv_files = glob.glob(os.path.join(folder_path, "clients_*.csv"))
    
    if not csv_files:
        raise FileNotFoundError(f"No se encontraron archivos clients_*.csv en {folder_path}")
    
    dfs = [pd.read_csv(f) for f in csv_files]
    consolidated = pd.concat(dfs, ignore_index=True)
    
    # Convertir fecha a datetime (simple y robusto)
    consolidated['fecha_email'] = pd.to_datetime(consolidated['fecha_email'], errors='coerce')
    
    # Remover duplicados por id_email (mantener el más reciente)
    consolidated = consolidated.sort_values('fecha_email').drop_duplicates(
        subset=['id_email'], keep='last'
    )
    
    return consolidated


def create_general_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea pestaña de resumen general.
    
    Args:
        df: DataFrame consolidado
        
    Returns:
        DataFrame con resumen general
    """
    summary = df[['remitente', 'asunto', 'score', 'sentimiento', 'evidencia', 'fecha_email']].copy()
    summary = summary.sort_values('fecha_email', ascending=False)
    return summary


def create_client_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea análisis agrupado por cliente.
    
    Incluye:
    - Número de contactos
    - Timeline (primer/último contacto)
    - Estadísticas de scores
    - Tendencia (mejora/empeora/estable)
    - Temas principales
    - Bandera de alerta
    
    Args:
        df: DataFrame consolidado
        
    Returns:
        DataFrame con análisis por cliente
    """
    client_groups = df.groupby('remitente', as_index=False).agg({
        'id_email': 'count',
        'score': ['min', 'max', 'mean'],
        'sentimiento': lambda x: (x == 'descontento').sum(),
        'fecha_email': ['min', 'max'],
        'asunto': lambda x: ' | '.join([str(s) for s in x.unique()[:3] if pd.notna(s)])  # Primeros 3 temas sin NaN
    })
    
    # Aplanar los nombres de columnas multinivel
    client_groups.columns = ['remitente', 'num_contactos', 'score_minimo', 'score_maximo', 
        'score_promedio', 'num_descontento', 'primer_contacto', 'ultimo_contacto', 'temas']
    
    # Calcular tendencia (últimos 2 contactos)
    def get_tendency(remitente):
        client_emails = df[df['remitente'] == remitente].sort_values('fecha_email')
        if len(client_emails) < 2:
            return '→ (único)'
        
        scores = client_emails['score'].values
        if scores[-1] > scores[-2] + 0.1:
            return '📈 (empeora)'
        elif scores[-1] < scores[-2] - 0.1:
            return '📉 (mejora)'
        else:
            return '→ (estable)'
    
    client_groups.loc[:, 'tendencia'] = client_groups['remitente'].apply(get_tendency)
    
    # Bandera de alerta
    def get_alert(row):
        alerts = []
        if row['num_descontento'] >= 2:
            alerts.append('⚠️ Múltiples descontentos')
        if row['score_maximo'] >= 0.8 and row['num_contactos'] >= 2:
            alerts.append('🚨 Escalada detectada')
        if row['num_contactos'] >= 3 and row['score_promedio'] >= 0.6:
            alerts.append('📍 Cliente recurrente insatisfecho')
        if row['score_minimo'] >= 0.7:
            alerts.append('⛔ Mínimo de satisfacción bajo')
        
        return ' | '.join(alerts) if alerts else '✓'
    
    client_groups.loc[:, 'alerta'] = client_groups.apply(get_alert, axis=1)
    
    # Recomendación basada en alerta
    def get_recommendation(alerta_str):
        if '🚨' in alerta_str:
            return 'CONTACTO URGENTE'
        elif '⚠️' in alerta_str:
            return 'Revisión prioritaria'
        elif '📍' in alerta_str:
            return 'Seguimiento'
        else:
            return 'Monitorear'
    
    client_groups.loc[:, 'recomendacion'] = client_groups['alerta'].apply(get_recommendation)
    
    # Limpiar columnas
    client_groups.loc[:, 'score_promedio'] = client_groups['score_promedio'].round(2)
    # Convertir fechas de forma robusta (manejar timezone-aware)
    client_groups.loc[:, 'primer_contacto'] = pd.to_datetime(client_groups['primer_contacto'], utc=True).dt.tz_localize(None).dt.strftime('%Y-%m-%d')
    client_groups.loc[:, 'ultimo_contacto'] = pd.to_datetime(client_groups['ultimo_contacto'], utc=True).dt.tz_localize(None).dt.strftime('%Y-%m-%d')
    
    return client_groups.sort_values('score_promedio', ascending=False)


def create_critical_cases(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica casos críticos para revisión manual.
    
    Criterios:
    - Múltiples contactos + escalada de insatisfacción
    - Múltiples contactos descontento
    - Cambio abrupto (neutral → descontento)
    
    Args:
        df: DataFrame consolidado
        
    Returns:
        DataFrame con casos críticos ordenados por severidad
    """
    critical = []
    
    for remitente in df['remitente'].unique():
        client_emails = df[df['remitente'] == remitente].sort_values('fecha_email')
        
        # Filtrar registros con fecha válida
        client_emails = client_emails.dropna(subset=['fecha_email'])
        
        if len(client_emails) < 2:
            continue
        
        # Criterio 1: Múltiples descontentos
        num_descontentos = (client_emails['sentimiento'] == 'descontento').sum()
        if num_descontentos >= 2:
            critical.append({
                'remitente': remitente,
                'criterio': 'Múltiples descontentos',
                'num_contactos': len(client_emails),
                'descontentos': num_descontentos,
                'score_promedio': client_emails['score'].mean(),
                'tendencia': 'Escalada' if client_emails['score'].iloc[-1] > client_emails['score'].iloc[-2] else 'Mejora',
                'primer_contacto': client_emails['fecha_email'].min().strftime('%Y-%m-%d'),
                'ultimo_contacto': client_emails['fecha_email'].max().strftime('%Y-%m-%d'),
                'temas': ' | '.join([str(s) for s in client_emails['asunto'].unique()[:3] if pd.notna(s)])
            })
        
        # Criterio 2: Escalada significativa (neutral → descontento)
        scores = client_emails['score'].values
        if len(scores) >= 2 and scores[-1] >= 0.7 and scores[-2] <= 0.4:
            critical.append({
                'remitente': remitente,
                'criterio': 'Escalada abrupta',
                'num_contactos': len(client_emails),
                'descontentos': num_descontentos,
                'score_promedio': client_emails['score'].mean(),
                'tendencia': f"Subió de {scores[-2]:.1f} a {scores[-1]:.1f}",
                'primer_contacto': client_emails['fecha_email'].min().strftime('%Y-%m-%d'),
                'ultimo_contacto': client_emails['fecha_email'].max().strftime('%Y-%m-%d'),
                'temas': ' | '.join([str(s) for s in client_emails['asunto'].unique()[:3] if pd.notna(s)])
            })
        
        # Criterio 3: Alto promedio de scores
        if len(client_emails) >= 3 and client_emails['score'].mean() >= 0.7:
            critical.append({
                'remitente': remitente,
                'criterio': 'Insatisfacción persistente',
                'num_contactos': len(client_emails),
                'descontentos': num_descontentos,
                'score_promedio': client_emails['score'].mean(),
                'tendencia': '⚠️ Persistente',
                'primer_contacto': client_emails['fecha_email'].min().strftime('%Y-%m-%d'),
                'ultimo_contacto': client_emails['fecha_email'].max().strftime('%Y-%m-%d'),
                'temas': ' | '.join([str(s) for s in client_emails['asunto'].unique()[:3] if pd.notna(s)])
            })
    
    if not critical:
        return pd.DataFrame()
    
    critical_df = pd.DataFrame(critical)
    critical_df['score_promedio'] = critical_df['score_promedio'].round(2)
    
    # Remover duplicados (mismo remitente, múltiples criterios)
    critical_df = critical_df.drop_duplicates(subset=['remitente'], keep='first')
    
    return critical_df.sort_values('score_promedio', ascending=False)

def _make_timezone_naive(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte todas las columnas datetime a string ISO para Excel (evita problemas de timezone y formato)."""
    df = df.copy()
    for col in df.columns:
        try:
            if hasattr(df[col], 'dt'):
                # Convertir datetime a string ISO
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            pass  # Ignorar columnas que no se pueden procesar
    return df


def generate_excel_report(folder_path: str, output_file: str = None) -> str:
    """
    Genera reporte Excel con múltiples pestañas.
    
    Args:
        folder_path: Directorio con los CSVs
        output_file: Nombre del archivo Excel (default: consolidado_evolucion.xlsx)
        
    Returns:
        Ruta del archivo generado
    """
    if output_file is None:
        output_file = os.path.join(folder_path, "consolidado_evolucion.xlsx")
    
    print("📊 Cargando datos...")
    df = load_all_csvs(folder_path)
    print(f"✓ {len(df)} emails únicos")
    
    print("📈 Generando resumen general...")
    summary = create_general_summary(df)
    
    print("📊 Análisis por cliente...")
    client_analysis = create_client_analysis(df)
    print(f"✓ {len(client_analysis)} clientes únicos")
    
    print("🚨 Identificando casos críticos...")
    critical = create_critical_cases(df)
    print(f"✓ {len(critical)} casos críticos encontrados")
    
    # Escribir Excel con múltiples hojas
    print(f"💾 Guardando en {output_file}...")
    
    # Asegurar que fecha_email es datetime naive antes de escribir
    for df_to_write in [summary, client_analysis, critical if not critical.empty else None]:
        if df_to_write is not None and 'fecha_email' in df_to_write.columns:
            df_to_write['fecha_email'] = pd.to_datetime(df_to_write['fecha_email'], errors='coerce')
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Convertir a timezone-naive antes de escribir
        summary = _make_timezone_naive(summary)
        client_analysis = _make_timezone_naive(client_analysis)
        critical = _make_timezone_naive(critical) if not critical.empty else critical
        
        summary.to_excel(writer, sheet_name='Todos los emails', index=False)
        client_analysis.to_excel(writer, sheet_name='Análisis por cliente', index=False)
        if not critical.empty:
            critical.to_excel(writer, sheet_name='Casos críticos', index=False)
        else:
            pd.DataFrame({'Mensaje': ['✓ No hay casos críticos detectados']}).to_excel(
                writer, sheet_name='Casos críticos', index=False
            )
    
    print(f"✓ Reporte generado: {output_file}")
    return output_file


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    else:
        # Usar la carpeta más reciente en output/
        output_dirs = sorted([d for d in glob.glob("output/*") if os.path.isdir(d)], reverse=True)
        if not output_dirs:
            print("❌ No se encontraron carpetas de ejecución en output/")
            sys.exit(1)
        folder = output_dirs[0]
    
    generate_excel_report(folder)
