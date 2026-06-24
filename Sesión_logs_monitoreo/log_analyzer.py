
#!/usr/bin/env python3 

""" 

Analizador de Seguridad de Logs — FinTech Nova 

Detecta intentos de SQL Injection en el archivo de logs del servidor. 

Sesión 10: Automatización y Scripting 

""" 

  

import re         # Módulo de expresiones regulares 

import sys        # Para acceder a argumentos de línea de comandos y salida de errores 

from datetime import datetime  # Para registrar cuándo se generó el análisis 

  

# ── SECCIÓN 1: Configuración de patrones de detección ──────────────── 

# Cada patrón de regex representa una técnica de SQL Injection conocida. 

# Los patrones usan flags re.IGNORECASE para detectar variaciones en mayúsculas. 

SQL_INJECTION_PATTERNS = [ 

    (r"'\s*OR\s*'?1'?\s*=\s*'?1",        "Bypass de autenticación clásico (OR 1=1)"), 

    (r"'\s*--",                           "Comentario SQL para ignorar contraseña"), 

    (r"UNION\s+SELECT",               "Inyección UNION para extraer datos"), 

    (r"DROP\s+TABLE",                "Intento de eliminar tabla (Destructivo)"), 

    (r"EXEC\s*\(",                   "Ejecución de comandos del sistema"), 

    (r"INSERT\s+INTO.*SELECT",      "Inyección de datos desde otra tabla"), 

] 

  

# ── SECCIÓN 2: Función principal de análisis ───────────────────────── 

def analyze_log_file(log_path): 

    """ 

    Analiza un archivo de logs en busca de patrones de SQL Injection. 

    Retorna un diccionario con estadísticas y lista de incidentes. 

    """ 

    incidents       = []   # Almacenará cada incidente detectado 

    total_lines     = 0    # Contador total de líneas analizadas 

    suspicious_lines= 0    # Contador de líneas con incidentes 

  

    try: 

        with open(log_path, 'r', encoding='utf-8') as log_file: 

            # Iterar línea por línea (eficiente en memoria para archivos grandes) 

            for line_number, line in enumerate(log_file, start=1): 

                total_lines += 1 

                line = line.strip()  # Eliminar espacios y saltos de línea 

  

                if not line:  # Ignorar líneas vacías 

                    continue 

  

                # Verificar cada patrón contra la línea actual 

                for pattern, description in SQL_INJECTION_PATTERNS: 

                    if re.search(pattern, line, re.IGNORECASE): 

                        suspicious_lines += 1 

                        incidents.append({ 

                            'line_number' : line_number, 

                            'content'     : line, 

                            'attack_type' : description 

                        }) 

                        break  # Una detección por línea es suficiente 

  

    except FileNotFoundError: 

        print(f"[ERROR] Archivo no encontrado: {log_path}") 

        sys.exit(1) 

    except PermissionError: 

        print(f"[ERROR] Sin permiso para leer: {log_path}") 

        sys.exit(1) 

  

    return { 

        'total_lines'     : total_lines, 

        'suspicious_lines': suspicious_lines, 

        'clean_lines'     : total_lines - suspicious_lines, 

        'incidents'       : incidents 

    } 

  

# ── SECCIÓN 3: Función de presentación del reporte ─────────────────── 

def print_report(results, log_path): 

    """Imprime un reporte formateado con los resultados del análisis.""" 

    separator = "=" * 60 

    print(f"\n{separator}") 

    print(f"  REPORTE DE SEGURIDAD — FinTech Nova") 

    print(f"  Archivo analizado : {log_path}") 

    print(f"  Fecha de análisis : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 

    print(f"{separator}") 

    print(f"  Total líneas      : {results['total_lines']}") 

    print(f"  Líneas limpias    : {results['clean_lines']}") 

    print(f"  Incidentes        : {results['suspicious_lines']}") 

    print(f"{separator}\n") 

  

    if results['incidents']: 

        print("  ⚠️  INCIDENTES DETECTADOS:") 

        for i, incident in enumerate(results['incidents'], 1): 

            print(f"  [{i}] Línea {incident['line_number']}: {incident['attack_type']}") 

            print(f"      → {incident['content'][:80]}...")  # Truncar a 80 chars 

    else: 

        print("  ✅ No se detectaron incidentes. Logs limpios.") 

  

    print(f"\n{separator}\n") 

  

# ── SECCIÓN 4: Punto de entrada del script ─────────────────────────── 

if __name__ == "__main__": 

    log_file = "server.log"  # Archivo a analizar 

    print(f"[INFO] Iniciando análisis de seguridad del archivo: {log_file}") 

    results = analyze_log_file(log_file) 

    print_report(results, log_file) 

