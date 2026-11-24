import hashlib
import os
import shutil

ROOTS = ["/sdcard", "/storage/emulated/0"]
SKIP_PARTS = {"/Android/data", "/Android/obb", "/proc", "/sys", "/dev"}
EXTS = (".png", ".jpg", ".jpeg", ".webp")

def sha1_file(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        while True:
            b = f.read(65536)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

unique = {}
for base in ROOTS:
    if not os.path.exists(base):
        continue
    for cur, dirs, files in os.walk(base, topdown=True):
        norm = cur.replace("\\", "/")
        if any(s in norm for s in SKIP_PARTS):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in files:
            if fn.lower().endswith(EXTS):
                full = os.path.join(cur, fn)
                try:
                    st = os.stat(full)
                    if st.st_size > 1024:
                        d = sha1_file(full)
                        prev = unique.get(d)
                        if prev is None or st.st_mtime > prev[0]:
                            unique[d] = (st.st_mtime, full, st.st_size)
                except OSError:
                    pass

ordered = sorted(unique.values(), key=lambda x: x[0], reverse=True)
print("=== أحدث 5 صور فريدة على الهاتف ===")
for i, (mt, p, sz) in enumerate(ordered[:5]):
    print(f"[{i}] {p} ({sz} bytes)")

picked = ordered[:3]
names = ["icon0.png", "splash.png", "ui.png"]
for f in os.listdir("assets"):
    try:
        os.remove(os.path.join("assets", f))
    except OSError:
        pass

for idx, (mt, src, sz) in enumerate(picked):
    dst = os.path.join("assets", names[idx])
    shutil.copy2(src, dst)
    print(f"LOADED {names[idx]} <- {src} ({sz} bytes)")

if len(picked) < 3:
    print("WARNING: عدد الصور الفريدة أقل من 3؛ احفظ الصور المطلوبة في المعرض/التنزيلات ثم أعد تشغيل fetch_images.py.")
