# ════════════════════════════════════════════════════════════
# Dockerfile — FinTech Nova API (Optimizado y Seguro)
# Sesión 13 - Laboratorio 3
# ════════════════════════════════════════════════════════════

# 1. Imagen base ligera
FROM python:3.11-slim

LABEL maintainer="fintech-nova@empresa.com"
LABEL version="1.0.0"

# 2. Variables de entorno de rendimiento
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo
WORKDIR /app

# 4. Crear usuario seguro no-root (Principio de Mínimo Privilegio)
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser

# 5. Instalar dependencias del sistema de forma optimizada
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 6. Instalar requerimientos de Python (Uso de Caché)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copiar todo el código del proyecto
COPY . .

# 8. Darle la propiedad de los archivos al usuario seguro
RUN chown -R appuser:appgroup /app

# 9. Cambiar al usuario seguro
USER appuser

# 10. Documentar puerto
EXPOSE 8000

# 11. Monitoreo automático de salud (HEALTHCHECK)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 12. Comando de inicio apuntando a tu estructura real
CMD ["uvicorn", "Sesión_SQL_Inyection.main:app", "--host", "0.0.0.0", "--port", "8000"]