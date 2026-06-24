#!/usr/bin/env python3
"""
health_monitor.py — Monitor automático del endpoint /health
Consulta el servicio periódicamente y registra su estado.
"""
import requests # Para hacer peticiones HTTP al endpoint /health
import time # Para pausar entre verificaciones
import json # Para parsear la respuesta JSON
from datetime import datetime

# ── CONFIGURACIÓN ────────────────────────────────────────────────
API_URL = "http://localhost:8000/health" # URL del health check
CHECK_INTERVAL = 60 # Segundos entre cada verificación
LOG_FILE = "health_log.txt" # Archivo donde guardar el historial
TIMEOUT_SECONDS = 10 # Tiempo máximo para esperar respuesta

def check_health():
    """
    Consulta el endpoint /health y devuelve el resultado.
    Retorna un diccionario con: status, timestamp, detalles, y el tiempo de respuesta.
    """
    start_time = time.time() # Registrar cuándo empezó la petición
    try:
        response = requests.get(API_URL, timeout=TIMEOUT_SECONDS)
        elapsed_ms = (time.time() - start_time) * 1000 # Tiempo en ms
        # Parsear el cuerpo JSON de la respuesta
        data = response.json()
        return {
            "reachable" : True,
            "http_status" : response.status_code,
            "app_status" : data.get("status", "unknown"),
            "response_ms" : round(elapsed_ms, 1),
            "details" : data,
            "timestamp" : datetime.utcnow().isoformat()
        }
    except requests.exceptions.ConnectionError:
        # No se pudo conectar — el servidor está caído
        return {"reachable": False, "error": "Servidor no alcanzable", "timestamp": datetime.utcnow().isoformat()}
    except requests.exceptions.Timeout:
        # La petición tardó más de TIMEOUT_SECONDS
        return {"reachable": False, "error": "Timeout — respuesta demasiado lenta", "timestamp": datetime.utcnow().isoformat()}

def log_result(result):
    """Escribe el resultado de la verificación en el archivo de log."""
    with open(LOG_FILE, 'a') as f: # Modo 'a' = append (agregar al final)
        log_line = json.dumps(result) + '\n'
        f.write(log_line)

def print_status(result):
    """Imprime el estado en la consola con formato legible."""
    ts = result.get("timestamp", "?")[:19] # Solo fecha y hora, sin microsegundos
    if not result.get("reachable"):
        print(f"[{ts}] ❌ NO ALCANZABLE: {result.get('error')}")
    elif result["app_status"] == "healthy":
        print(f"[{ts}] ✅ SALUDABLE ({result['response_ms']}ms)")
    else:
        print(f"[{ts}] ⚠️ DEGRADADO: {result.get('details')}")

# ── LOOP PRINCIPAL ───────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Monitor iniciado. Verificando cada {CHECK_INTERVAL}s → {API_URL}")
    while True: # Bucle infinito — corre hasta que se detenga manualmente
        result = check_health()
        print_status(result)
        log_result(result)
        time.sleep(CHECK_INTERVAL) # Esperar antes de la siguiente verificación