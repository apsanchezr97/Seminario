# Importaciones necesarias
from fastapi import FastAPI, HTTPException
from datetime import datetime
import sqlite3 # Para verificar la base de datos
import os # Para verificar archivos y espacio en disco
import shutil # Para obtener información del uso del disco

app = FastAPI()

@app.get("/health") # Define la ruta del endpoint de salud
def health_check():
    """
    Verifica el estado de todos los componentes del sistema.
    Retorna 200 OK si todo funciona, 503 Service Unavailable si hay problemas.
    """
    # Diccionario que acumula el estado de cada componente
    checks = {}
    overall_status = "healthy" # Asume saludable hasta que algo falle

    # ── VERIFICACIÓN 1: Base de datos ───────────────────────────
    try:
        # Intenta abrir y consultar la base de datos
        conn = sqlite3.connect("database.db", timeout=5)
        conn.execute("SELECT 1") # Consulta mínima: solo verifica que la BD responde
        conn.close()
        checks["database"] = {"status": "ok", "message": "Conectada y respondiendo"}
    except Exception as e:
        # Si la BD falla, marca el estado general como degradado
        checks["database"] = {"status": "error", "message": str(e)}
        overall_status = "degraded"

    # ── VERIFICACIÓN 2: Espacio en disco ────────────────────────
    disk = shutil.disk_usage('/') # Uso del disco raíz
    disk_percent = (disk.used / disk.total) * 100
    disk_status = "ok" if disk_percent < 85 else "warning"
    
    if disk_percent > 95:
        disk_status = "critical"
        overall_status = "degraded"
        
    checks["disk"] = {"status": disk_status, "used_percent": round(disk_percent, 1)}

    # ── RESPUESTA FINAL ──────────────────────────────────────────
    response = {
        "status" : overall_status,
        "timestamp" : datetime.utcnow().isoformat() + "Z",
        "version" : "1.0.0",
        "checks" : checks
    }

    # Si el estado es degradado, retornar código HTTP 503
    if overall_status != "healthy":
        raise HTTPException(status_code=503, detail=response)

    return response