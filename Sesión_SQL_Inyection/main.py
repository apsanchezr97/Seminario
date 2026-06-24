from fastapi import FastAPI, Depends, HTTPException 
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware 
from fastapi.responses import JSONResponse 
import sqlite3 

# IMPORTACIÓN REAL: Apunta a la carpeta correcta de monitoreo
from Sesión_logs_monitoreo.health_check import run_all_checks

app = FastAPI(title="FinTech Nova - Secure API Practice") 
 
# --- 1. MIDDLEWARE DE SEGURIDAD (Defensa Perimetral) --- 
# app.add_middleware(HTTPSRedirectMiddleware) # Comentado para pruebas locales en Codespaces 
 
@app.middleware("http") 
async def add_security_headers(request, call_next): 
    response = await call_next(request) 
    response.headers["X-Content-Type-Options"] = "nosniff" 
    response.headers["X-Frame-Options"] = "DENY" 
    response.headers["X-XSS-Protection"] = "1; mode=block" 
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains" 
    response.headers["Content-Security-Policy"] = "default-src 'self'" 
    return response 
 
# --- 2. SETUP DE BASE DE DATOS EN MEMORIA --- 
def get_db(): 
    conn = sqlite3.connect(":memory:") 
    cursor = conn.cursor() 
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, role TEXT)") 
    cursor.executemany("INSERT INTO users (username, role) VALUES (?, ?)", 
                       [("admin", "superadmin"), ("juan", "user"), ("maria", "user")]) 
    conn.commit() 
    return conn 
 
# --- 3. ENDPOINT VULNERABLE (A03: Injection) --- 
@app.get("/vulnerable/users/{username}") 
def get_user_vulnerable(username: str): 
    conn = get_db() 
    cursor = conn.cursor() 
    # NUNCA HACER ESTO: Concatenacion directa 
    query = f"SELECT * FROM users WHERE username = '{username}'" 
    try: 
        cursor.execute(query) 
        result = cursor.fetchall() 
        return {"query_ejecutada": query, "resultado": result} 
    except Exception as e: 
        return {"error": str(e)} 
 
# --- 4. ENDPOINT SEGURO (Prepared Statements) --- 
@app.get("/secure/users/{username}") 
def get_user_secure(username: str): 
    conn = get_db() 
    cursor = conn.cursor() 
    # FORMA SEGURA: Parametrizacion 
    query = "SELECT * FROM users WHERE username = ?" 
    cursor.execute(query, (username,)) 
    result = cursor.fetchall() 
    return {"query_ejecutada": query, "resultado": result} 

# --- 5. ENDPOINT DE OBSERVABILIDAD AVANZADA (Bloque 2) --- 
@app.get("/health")
def health_endpoint():
    """
    Endpoint de salud del laboratorio integrador.
    Devuelve un reporte en formato JSON. Lanza código 503 si el estado es crítico.
    """
    result = run_all_checks()
    if result['status'] == 'unhealthy':
        raise HTTPException(status_code=503, detail=result)
    return result