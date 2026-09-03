#!/bin/bash
# Prepara l'ambiente per gli strumenti 3D (sessione nuova = container nuovo).
#
#   bash STRUMENTI_3D/setup_ambiente.sh              # librerie Python (~2 min)
#   bash STRUMENTI_3D/setup_ambiente.sh --libredwg   # + LibreDWG per LEGGERE i DWG (~4 min)
#
# LibreDWG serve solo se il file 2D arriva come DWG: dwg2dxf lo converte in DXF
# di lavoro (la LETTURA di LibreDWG e' stabile; la scrittura no, e infatti la
# pipeline non la usa per consegnare DWG).
set -e

echo "== Librerie Python (ezdxf, numpy, matplotlib, cadquery/OpenCASCADE) =="
pip install -q ezdxf numpy matplotlib cadquery
python3 -c "import ezdxf, cadquery; print('ezdxf', ezdxf.__version__, '| cadquery', cadquery.__version__)"

if [ "$1" = "--libredwg" ]; then
    if command -v dwg2dxf >/dev/null; then
        echo "== LibreDWG gia' presente: $(dwg2dxf --version 2>&1 | head -1) =="
    else
        echo "== Compilazione LibreDWG (lettura DWG) =="
        TMP=$(mktemp -d)
        curl -sL --max-time 180 -o "$TMP/libredwg.tar.gz" \
            https://github.com/LibreDWG/libredwg/releases/download/0.13.3/libredwg-0.13.3.tar.gz
        tar xzf "$TMP/libredwg.tar.gz" -C "$TMP"
        (cd "$TMP"/libredwg-* && ./configure --disable-bindings --disable-python \
            --enable-release --prefix=/usr/local >/dev/null 2>&1 \
            && make -j4 >/dev/null 2>&1 && make install >/dev/null 2>&1 && ldconfig)
        rm -rf "$TMP"
        echo "LibreDWG installato: $(dwg2dxf --version 2>&1 | head -1)"
    fi
fi
echo "== Pronto. Flusso veloce: vedi STRUMENTI_3D/README_3D.md =="
