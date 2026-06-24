#!/bin/bash
# ════════════════════════════════════════════════════════════
# Script: backup_db.sh | FinTech Nova | Sesión 13 - Lab 3
# Propósito: Respaldar database.db con timestamp y limpiar backups viejos
# Uso: ./Scripts/backup_db.sh
# ════════════════════════════════════════════════════════════

# ── SECCIÓN 1: Variables del script ─────────────────────────
# RUTA CORREGIDA: Apunta a donde realmente está tu base de datos
DB_FILE="Sesión_logs_monitoreo/database.db" 
BACKUP_DIR="backups" # Carpeta donde guardar los backups
RETENTION_DAYS=7 # Días de backups a conservar
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S") # Ej: 2024-11-15_02-30-00
BACKUP_FILE="backup_${TIMESTAMP}.tar.gz" # Nombre único del backup

# ── SECCIÓN 2: Función de logging ───────────────────────────
log() {
 echo "[$(date +"%H:%M:%S")] $1"
}

# ── SECCIÓN 3: Verificaciones previas ───────────────────────
log "Iniciando backup de FinTech Nova..."
if [ ! -f "$DB_FILE" ]; then
 log "ERROR: No se encontró $DB_FILE. Abortando."
 exit 1
fi

# Calcular tamaño del archivo antes del backup
DB_SIZE=$(du -sh "$DB_FILE" | cut -f1)
log "Archivo encontrado: $DB_FILE ($DB_SIZE)"

# ── SECCIÓN 4: Crear directorio de backups ───────────────────
if [ ! -d "$BACKUP_DIR" ]; then
 log "Creando directorio de backups: $BACKUP_DIR"
 mkdir -p "$BACKUP_DIR"
fi

# ── SECCIÓN 5: Crear el backup comprimido ────────────────────
log "Creando backup: $BACKUP_DIR/$BACKUP_FILE"
tar -czf "$BACKUP_DIR/$BACKUP_FILE" "$DB_FILE"

# $? contiene el código de salida del último comando (0 = éxito)
if [ $? -eq 0 ]; then
 BACKUP_SIZE=$(du -sh "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
 log "OK: Backup creado exitosamente ($BACKUP_SIZE)"
else
 log "ERROR: Falló la creación del backup. Revisa el espacio en disco."
 exit 1
fi

# ── SECCIÓN 6: Limpiar backups antiguos ─────────────────────
BACKUP_COUNT=$(ls "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
log "Backups existentes: $BACKUP_COUNT (reteniendo últimos $RETENTION_DAYS)"
find "$BACKUP_DIR" -name "*.tar.gz" -mtime "+$RETENTION_DAYS" -delete
log "Limpieza de backups antiguos completada."
log "Proceso de backup finalizado correctamente."
exit 0

