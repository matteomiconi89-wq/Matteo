#!/usr/bin/env bash
# ============================================================================
#  genera_step.sh — DAL DWG 2D A TUTTI GLI STEP, CON UNA SOLA PAROLA.
#  Uso:   ./genera_step.sh [PIANTA.dwg|.dxf] [PROGETTO.dwg|.dxf] [OUT_DIR]
#  Senza argomenti usa:
#     PIANTA   = ../26A011_PIANTA_GENERALE.dwg   (pianta con arredo assemblato)
#     PROGETTO = (assente -> la cucina viene riusata dagli STEP gia' generati)
#     OUT_DIR  = ../cad
#  Produce:  OUT_DIR/step/*.step (uno per mobile) + OUT_DIR/26A011_arredo_completo.step
#            + pipeline/arredo_geometry_mobili.json (mesh per il viewer 3D)
# ============================================================================
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PIANTA="${1:-$HERE/../26A011_PIANTA_GENERALE.dwg}"
PROGETTO="${2:-$HERE/../PROGETTO_INESISTENTE.dxf}"
OUT="${3:-$HERE/../cad}"

# 1) dipendenze python (idempotente)
python3 -c "import cadquery, shapely, ezdxf" 2>/dev/null || pip install --quiet cadquery shapely ezdxf

# 2) converti DWG->DXF se serve (LibreDWG). Ordine di ricerca: bundle pipeline/bin, PATH, apt.
dwg2dxf_bin=""
for c in "$HERE/bin/dwg2dxf" "$(command -v dwg2dxf || true)"; do
  [ -n "$c" ] && [ -x "$c" ] && { dwg2dxf_bin="$c"; break; }
done
to_dxf () {  # $1 input -> stampa il path .dxf
  local f="$1"
  case "$f" in
    *.dxf|*.DXF) echo "$f" ;;
    *.dwg|*.DWG)
      local out="${TMPDIR:-/tmp}/$(basename "${f%.*}").dxf"
      if [ -z "$dwg2dxf_bin" ]; then
        echo "ERRORE: serve LibreDWG (dwg2dxf) per convertire $f. Installa: apt-get install libredwg-tools" >&2
        exit 3
      fi
      "$dwg2dxf_bin" -o "$out" "$f" >&2
      echo "$out" ;;
    *) echo "$f" ;;
  esac
}
PIANTA_DXF="$(to_dxf "$PIANTA")"
if [ -f "$PROGETTO" ]; then PROGETTO_DXF="$(to_dxf "$PROGETTO")"; else PROGETTO_DXF="$PROGETTO"; fi

# 3) ricostruzione: uno STEP per mobile + assieme + mesh viewer
python3 "$HERE/ricostruisci.py" "$PIANTA_DXF" "$PROGETTO_DXF" "$OUT"
