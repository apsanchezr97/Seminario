#!/usr/bin/env python3
"""
health_check.py — Lógica de verificación de salud y Endpoint de FastAPI para FinTech Nova
Sesión 13 - Laboratorio 3
"""
from fastapi import FastAPI, HTTPException
import sqlite3
import shutil  # Para verificar espacio en disco
import os
import time
from datetime import datetime
from typing import Tuple

app = FastAPI(title="FinTech Nova Health Monitoring Service")

# ── FUNCIONES DE VERIFICACIÓN ─────────────────────────────────

def check_database(db_path: str = 'Sesión_logs_monitoreo/database.db') -> Tuple[str, str]:
    """Verifica que la base de datos esté accesible y responda rápido."""
    # Intentar buscar en raíz si falla la ruta interna por contextos de ejecución
    if not os.path.exists(db_path) and os.path.exists('database.db'):
        db_path = 'database.db'
        
    if not os.path.exists(db_path):
        return 'error', f'Archivo de BD no encontrado: {db_path}'
    try:
        start = time.time()
        conn = sqlite3.connect(db_path, timeout=5)
        conn.execute('SELECT 1')  # Consulta mínima de verificación
        conn.close()
        elapsed_ms = (time.time() - start) * 1000
        if elapsed_ms > 500:
            return 'warning', f'BD lenta: {elapsed_ms:.1f}ms (límite: 500ms)'
        return 'ok', f'BD accesible y respondiendo en {elapsed_ms:.1f}ms'
    except sqlite3.OperationalError as e:
        return 'error', f'Error al conectar con BD: {e}'

def check_disk(path: str = '/', warn_pct: int = 80, crit_pct: int = 95) -> Tuple[str, str]:
    """Verifica el espacio disponible en disco."""
    try:
        usage = shutil.disk_usage(path)
        used_pct = (usage.used / usage.total) * 100
        free_gb = usage.free / (1024**3)  # Convertir bytes a GB
        if used_pct >= crit_pct:
            return 'error', f'Disco crítico: {used_pct:.1f}% usado ({free_gb:.1f}GB libre)'
        if used_pct >= warn_pct:
            return 'warning', f'Disco alto: {used_pct:.1f}% usado ({free_gb:.1f}GB libre)'
        return 'ok', f'Disco saludable: {used_pct:.1f}% usado ({free_gb:.1f}GB libre)'
    except Exception as e:
        return 'error', f'No se pudo verificar disco: {e}'

def check_backup(backup_dir: str = 'backups', max_age_hours: int = 25) -> Tuple[str, str]:
    """Verifica la existencia y frescura del backup generado por el script Bash."""
    if not os.path.isdir(backup_dir):
        return 'warning', f'Directorio de backups no existe: {backup_dir}'
    backups = sorted([
        f for f in os.listdir(backup_dir) if f.endswith('.tar.gz')
    ])
    if not backups:
        return 'error', 'No se encontraron backups en el directorio'
    latest = backups[-1]
    latest_path = os.path.join(backup_dir, latest)
    age_hours = (time.time() - os.path.getmtime(latest_path)) / 3600
    if age_hours > max_age_hours:
        return 'warning', f'Backup más reciente tiene {age_hours:.1f}h (máx: {max_age_hours}h)'
    return 'ok', f'Backup reciente: {latest} ({age_hours:.1f}h de antigüedad)'

def run_all_checks() -> dict:
    """Consolida todos los diagnósticos en un único reporte json."""
    checks = {}
    db_status, db_msg = check_database()
    disk_status, disk_msg = check_disk()
    bkp_status, bkp_msg = check_backup()
    
    checks['database'] = {'status': db_status, 'message': db_msg}
    checks['disk'] = {'status': disk_status, 'message': db_msg} # Alineado a la estructura de la guía
    checks['backup'] = {'status': bkp_status, 'message': bkp_msg}
    
    all_statuses = [checks[k]['status'] for k in checks]
    if 'error' in all_statuses:
        overall = 'unhealthy'
    elif 'warning' in all_statuses:
        overall = 'degraded'
    else:
        overall = 'healthy'
        
    return {
        'status': overall,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': '1.0.0',
        'checks': checks,
    }

# ── ENDPOINT FASTAPI ──────────────────────────────────────────

@app.get("/health")
def health_endpoint():
    """Endpoint de salud pública. Retorna 503 si el sistema está comprometido."""
    result = run_all_checks()
    if result['status'] == 'unhealthy':
        raise HTTPException(status_code=503, detail=result)
    return result

# Permite probarlo de forma independiente ejecutando python3
if __name__ == '__main__':
    import json
    print("[INFO] Ejecutando diagnósticos rápidos desde consola:")
    print(json.dumps(run_all_checks(), indent=2, ensure_ascii=False))