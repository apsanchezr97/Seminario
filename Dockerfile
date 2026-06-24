# ── ETAPA 1: Imagen base ─────────────────────────────────────────
# FROM: especifica qué imagen usar como punto de partida.
# python:3.11-slim es Python 3.11 sobre Debian Linux mínimo (sin apps innecesarias).
# 'slim' reduce el tamaño de la imagen de ~900MB a ~130MB.
FROM python:3.11-slim

# ── ETAPA 2: Directorio de trabajo ───────────────────────────────
# WORKDIR: establece el directorio de trabajo dentro del contenedor.
# Todos los COPY y CMD siguientes operan relativo a este directorio.
WORKDIR /app

# ── ETAPA 3: Copiar lista de dependencias PRIMERO ────────────────
# Por qué copiar requirements.txt antes que el código?
# Docker cachea cada capa. Si solo cambia el código (no las deps),
# Docker reutiliza la capa de instalación de deps — build más rápido.
COPY requirements.txt .

# ── ETAPA 4: Instalar dependencias ──────────────────────────────
# RUN ejecuta un comando durante el proceso de BUILD de la imagen.
# --no-cache-dir: no guarda cache de pip (reduce tamaño de imagen).
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# ── ETAPA 5: Copiar el código de la aplicación ────────────────────
# COPY <origen_en_tu_máquina> <destino_en_el_contenedor>
# El punto '.' como destino significa 'el WORKDIR actual' (/app).
COPY . .

# ── ETAPA 6: Exponer el puerto ────────────────────────────────────
# EXPOSE documenta en qué puerto escucha la aplicación.
# NO abre el puerto al exterior — eso lo hace 'docker run -p'.
# Es documentación para quien lee el Dockerfile.
EXPOSE 8000

# ── ETAPA 7: Variables de entorno ────────────────────────────────
# ENV define variables de entorno disponibles dentro del contenedor.
# PYTHONUNBUFFERED=1: los prints de Python aparecen en los logs inmediatamente.
ENV PYTHONUNBUFFERED=1

# ── ETAPA 8: Health check de Docker ─────────────────────────────
# Docker puede verificar automáticamente la salud del contenedor.
# interval: verificar cada 30 segundos.
# timeout: el health check falla si no responde en 10s.
# retries: después de 3 fallos consecutivos, el contenedor es 'unhealthy'.
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
 CMD curl -f http://localhost:8000/health || exit 1

# ── ETAPA 9: Comando de inicio ───────────────────────────────────
# CMD define el comando que se ejecuta cuando se INICIA el contenedor.
# A diferencia de RUN (que corre durante el build), CMD corre en cada inicio.
# --host 0.0.0.0: escuchar en todas las interfaces de red (necesario en Docker).
CMD ["uvicorn", "Sesión_logs_monitoreo.health_check:app", "--host", "0.0.0.0", "--port", "8000"]