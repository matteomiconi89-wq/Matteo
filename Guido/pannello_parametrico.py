#!/usr/bin/env python3
"""
pannello_parametrico.py
Ridimensiona pannelli 3D solidi in AutoCAD 2025 lungo un asse.

COME USARE:
  1. Aprire il file DWG in AutoCAD 2025
  2. Eseguire questo script: python pannello_parametrico.py
  3. Inserire le dimensioni richieste

REQUISITI:
  pip install pywin32
"""

import sys

try:
    import win32com.client
    import pythoncom
except ImportError:
    print("ERRORE: pywin32 non installato.")
    print("Eseguire: pip install pywin32")
    input("\nPremi Invio per uscire...")
    sys.exit(1)


def a_double(values):
    """Crea un VARIANT array di double per AutoCAD COM."""
    return win32com.client.VARIANT(
        pythoncom.VT_ARRAY | pythoncom.VT_R8,
        list(values)
    )


def get_bbox(entity):
    """Restituisce (min_pt, max_pt) come liste Python."""
    bb = entity.GetBoundingBox()
    return list(bb[0]), list(bb[1])


def main():
    print("=" * 55)
    print("   PANNELLO PARAMETRICO  -  AutoCAD 2025")
    print("=" * 55)

    # ── Connessione ad AutoCAD ──────────────────────────────
    try:
        acad = win32com.client.GetActiveObject("AutoCAD.Application")
        doc  = acad.ActiveDocument
        msp  = doc.ModelSpace
        print(f"\nConnesso a: {doc.Name}")
    except Exception as e:
        print("\nERRORE: AutoCAD non trovato o non aperto.")
        print(f"Dettaglio: {e}")
        input("\nPremi Invio per uscire...")
        sys.exit(1)

    # ── Parametri utente ────────────────────────────────────
    print("\n─── DIMENSIONI ───────────────────────────────────────")
    try:
        old_w = float(input("Larghezza ATTUALE (mm)  [es. 600]: ").strip() or "600")
        new_w = float(input("Larghezza NUOVA   (mm)  [es. 580]: ").strip() or "580")
    except ValueError:
        print("Valore non valido.")
        input("Premi Invio per uscire...")
        sys.exit(1)

    delta = new_w - old_w

    axis_input = input("Asse da ridimensionare (X / Y / Z) [X]: ").strip().upper() or "X"
    axis = {"X": 0, "Y": 1, "Z": 2}.get(axis_input, 0)

    print(f"\n  Variazione : {delta:+.2f} mm")
    print(f"  Asse       : {axis_input}")

    # ── Raccolta solidi 3D ──────────────────────────────────
    solids = []
    for i in range(msp.Count):
        try:
            ent = msp.Item(i)
            if ent.EntityName in ("AcDb3dSolid", "AcDbBody"):
                solids.append(ent)
        except Exception:
            pass

    if not solids:
        print("\nNessun solido 3D trovato nel disegno.")
        input("Premi Invio per uscire...")
        return

    print(f"\nTrovati {len(solids)} solidi 3D.")

    # ── Bounding box globale ────────────────────────────────
    g_min = [float("inf")]  * 3
    g_max = [float("-inf")] * 3

    for s in solids:
        mn, mx = get_bbox(s)
        for i in range(3):
            g_min[i] = min(g_min[i], mn[i])
            g_max[i] = max(g_max[i], mx[i])

    total_span = g_max[axis] - g_min[axis]
    threshold  = g_min[axis] + total_span * 0.5
    tolerance  = total_span * 0.08   # 8% di tolleranza per "pannello passante"

    print(f"\n  Dimensione asse {axis_input} : {total_span:.2f} mm")
    print(f"  Da {g_min[axis]:.2f}  a  {g_max[axis]:.2f}")
    print(f"  Soglia destra/sinistra : {threshold:.2f} mm")

    # ── Classificazione solidi ──────────────────────────────
    #
    #  TIPO A – Pannello "destro"
    #    Il centro è oltre la soglia e NON attraversa tutto il range.
    #    → viene SPOSTATO di delta.
    #
    #  TIPO B – Pannello "passante" (ripiani, fondo, traversi)
    #    Si estende per quasi tutta la larghezza.
    #    → va ACCORCIATO: spostare solo la faccia destra.
    #
    #  TIPO C – Pannello "sinistro"
    #    Il centro è prima della soglia e non è passante.
    #    → rimane fermo.
    #

    print("\n─── ELABORAZIONE ─────────────────────────────────────")

    moved     = 0   # pannelli spostati
    to_resize = []  # pannelli da ridimensionare manualmente

    for s in solids:
        mn, mx  = get_bbox(s)
        s_min   = mn[axis]
        s_max   = mx[axis]
        center  = (s_min + s_max) / 2.0

        is_spanning = (s_min < g_min[axis] + tolerance and
                       s_max > g_max[axis] - tolerance)

        if is_spanning:
            # TIPO B – registra per istruzioni manuali
            to_resize.append(s)

        elif center > threshold:
            # TIPO A – sposta verso sinistra/destra
            mv = [0.0, 0.0, 0.0]
            mv[axis] = delta
            s.Move(a_double([0.0, 0.0, 0.0]), a_double(mv))
            moved += 1

        # TIPO C – non toccare

    # ── Risultati ───────────────────────────────────────────
    print(f"\n  ✓ Spostati    : {moved} pannelli laterali  ({delta:+.0f} mm)")
    print(f"  ⚠ Da ridurre  : {len(to_resize)} pannelli passanti")

    if to_resize:
        print()
        print("─── PANNELLI DA RIDIMENSIONARE MANUALMENTE ───────────")
        print("  Questi pannelli coprono tutta la larghezza")
        print(f"  (ripiani, fondo, traversi) e devono essere accorciati")
        print(f"  di {abs(delta):.0f} mm sul lato {'sinistro' if delta < 0 else 'destro'}.")
        print()
        print("  Procedura veloce in AutoCAD:")
        print("  1. Clicca sul pannello")
        print("  2. Passa il mouse sulla freccia GRIP sul lato da accorciare")
        print(f"  3. Clicca e digita  {delta:+.0f}  poi Invio")
        print()
        print("  Oppure usa SOLIDEDIT > Face > Move > seleziona la faccia")

    # ── Rigenera disegno ────────────────────────────────────
    try:
        doc.Regen(0)
    except Exception:
        pass

    print("\n" + "=" * 55)
    print("  FATTO! Controlla il risultato in AutoCAD.")
    print("=" * 55)
    input("\nPremi Invio per uscire...")


if __name__ == "__main__":
    main()
