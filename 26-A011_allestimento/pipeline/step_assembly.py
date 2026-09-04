#!/usr/bin/env python3
"""Lettore di assiemi STEP con NOMI dei pezzi (XCAF/XDE).

Legge uno STEP esportato dal CAD di Matteo e restituisce, per ogni pezzo
effettivamente posizionato nell'assieme, il suo NOME (codice distinta, es.
"26-A011_AM_73_VELETTA") e il solido gia' trasformato nella posizione giusta.

Uso:
    from step_assembly import read_assembly
    parts = read_assembly("26A011_ArmadioCameraMaster.stp")   # [(nome, TopoDS_Shape), ...]
"""
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer


def _name(lab):
    a = TDataStd_Name()
    if lab.FindAttribute(TDataStd_Name.GetID_s(), a):
        return str(a.Get().ToExtString())
    return "?"


def _walk(st, lab, loc, out):
    """Scende nell'albero assieme accumulando le trasformazioni."""
    if st.IsAssembly_s(lab):
        comps = TDF_LabelSequence()
        st.GetComponents_s(lab, comps)
        for i in range(1, comps.Length() + 1):
            c = comps.Value(i)
            cloc = st.GetLocation_s(c)
            nl = loc.Multiplied(cloc)
            ref = TDF_Label()
            if st.GetReferredShape_s(c, ref):
                _walk(st, ref, nl, out)
            else:
                _walk(st, c, nl, out)
    else:
        sh = st.GetShape_s(lab)
        if sh.IsNull():
            return
        sh = sh.Moved(loc)
        ex = TopExp_Explorer(sh, TopAbs_SOLID)
        if not ex.More():
            return                      # scarta gli "Skeleton" (senza solidi)
        out.append((_name(lab), sh))


def read_assembly(path):
    doc = TDocStd_Document(TCollection_ExtendedString("d"))
    r = STEPCAFControl_Reader()
    r.SetNameMode(True); r.SetColorMode(True); r.SetLayerMode(True)
    r.ReadFile(path); r.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    roots = TDF_LabelSequence(); st.GetFreeShapes(roots)
    out = []
    for i in range(1, roots.Length() + 1):
        _walk(st, roots.Value(i), TopLoc_Location(), out)
    return out


def solid_count(sh):
    ex = TopExp_Explorer(sh, TopAbs_SOLID); n = 0
    while ex.More():
        n += 1; ex.Next()
    return n


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        parts = read_assembly(p)
        print(f"\n{p}: {len(parts)} pezzi posizionati, {sum(solid_count(s) for _, s in parts)} solidi")
        from collections import Counter
        for n, c in Counter(n for n, _ in parts).most_common():
            print(f"   {c:3d} x  {n}")
