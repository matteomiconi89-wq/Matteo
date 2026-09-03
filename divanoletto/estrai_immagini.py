# -*- coding: utf-8 -*-
"""Estrae le immagini base64 dai transcript .jsonl della sessione Claude Code
e le salva come file PNG/JPG nella cartella divanoletto, per poterle elaborare."""
import os, json, base64, hashlib, glob

here = os.path.dirname(os.path.abspath(__file__))
proj = os.path.join(os.environ["USERPROFILE"], ".claude", "projects", "C--Users-User")
jsonls = sorted(glob.glob(os.path.join(proj, "*.jsonl")), key=os.path.getmtime, reverse=True)

try:
    from PIL import Image
    import io
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

found = {}   # md5 -> info

def walk(node):
    if isinstance(node, dict):
        mt = node.get("media_type") or node.get("mediaType")
        data = node.get("data")
        if isinstance(mt, str) and mt.startswith("image/") and isinstance(data, str) and len(data) > 100:
            yield mt, data
        # source nesting
        for v in node.values():
            yield from walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk(v)

for jf in jsonls[:6]:
    try:
        with open(jf, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                for mt, data in walk(obj):
                    try:
                        raw = base64.b64decode(data)
                    except Exception:
                        continue
                    h = hashlib.md5(raw).hexdigest()
                    if h in found:
                        continue
                    ext = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp",
                           "image/gif": "gif"}.get(mt, "bin")
                    dim = ""
                    if HAVE_PIL:
                        try:
                            im = Image.open(io.BytesIO(raw))
                            dim = "%dx%d" % im.size
                        except Exception:
                            dim = "?"
                    fn = "estratta_%02d_%s.%s" % (len(found) + 1, h[:8], ext)
                    fp = os.path.join(here, fn)
                    with open(fp, "wb") as out:
                        out.write(raw)
                    found[h] = (fn, mt, len(raw), dim, os.path.basename(jf))
    except Exception as e:
        print("skip", os.path.basename(jf), e)

print("Trovate %d immagini uniche:" % len(found))
for h, (fn, mt, n, dim, src) in found.items():
    print("  %-26s %-11s %8d bytes  %-10s  <- %s" % (fn, mt, n, dim, src))
