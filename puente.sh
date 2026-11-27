#!/usr/bin/env bash
# Trae archivos de internet a la sesión por la rama puente-instagram del repositorio.
# Hace falta porque la sesión no llega directo a los servidores de Runway: una automatización
# de GitHub baja los archivos, los deja en la rama y la sesión los toma de ahí.
#
# Uso: bash puente.sh lista.tsv carpeta_destino
#   lista.tsv: un renglón por archivo, "nombre<TAB>url" (la url completa, con su firma).
# Al terminar deja la rama como estaba (los archivos no quedan publicados).
#
# Variables opcionales:
#   PUENTE_DIR      carpeta local de la rama puente (por defecto /home/claude/work/puente)
#   REPO_URL        repositorio (por defecto el del sitio)
#   COMMIT_TRAILER  renglones de atribución para el mensaje del commit, si la sesión los pide
set -euo pipefail
LIST="$(realpath "$1")"
DEST="$(realpath -m "$2")"
PUENTE_DIR="${PUENTE_DIR:-/home/claude/work/puente}"
REPO_URL="${REPO_URL:-https://github.com/fededst68-commits/Sitio-Web.git}"
if [ ! -d "$PUENTE_DIR/.git" ] && [ ! -f "$PUENTE_DIR/.git" ]; then
  git clone -q --branch puente-instagram --single-branch "$REPO_URL" "$PUENTE_DIR"
fi
cd "$PUENTE_DIR"
git fetch -q origin puente-instagram
git checkout -q -B puente-instagram origin/puente-instagram
CLEAN=$(git rev-parse HEAD)
cp "$LIST" pedido/urls.txt
git add pedido/urls.txt
if [ -n "${COMMIT_TRAILER:-}" ]; then
  git commit -q -m "Pedido de archivos para la edición" -m "$COMMIT_TRAILER"
else
  git commit -q -m "Pedido de archivos para la edición"
fi
git push -q origin puente-instagram
PED=$(git rev-parse HEAD)
ok=0
for i in $(seq 1 45); do
  sleep 5
  git fetch -q origin puente-instagram
  if [ "$(git rev-parse origin/puente-instagram)" != "$PED" ]; then ok=1; break; fi
done
if [ "$ok" = 1 ]; then
  git pull -q --ff-only origin puente-instagram
  mkdir -p "$DEST"
  head -2 media/RESULTADO.txt
  for f in media/*; do
    [ "$(basename "$f")" = "RESULTADO.txt" ] || cp "$f" "$DEST"/
  done
else
  echo "el puente no respondió a tiempo"
fi
git reset -q --hard "$CLEAN"
git push -q --force origin puente-instagram
echo "rama limpia: $(git log --oneline -1)"
ls -la "$DEST" 2>/dev/null || true
