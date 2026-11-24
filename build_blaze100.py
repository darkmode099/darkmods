import hashlib
import os
import shutil
import subprocess
import sys

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(65536)
            if not b:
                break
            h.update(b)
    return h.hexdigest()[:12]

def main():
    project_dir = os.path.abspath(os.path.dirname(__file__))
    os.chdir(project_dir)

    print("====================================================")
    print("        BLAZE 100 - LOCAL BUILD & PACKAGER")
    print("====================================================")

    # 1. تشغيل الفحص والحماية المسبقة أولاً
    subprocess.run([sys.executable, "auto_guard_build.py"], check=True)

    bundle_root = os.path.join("pkg_output", "Blaze100_Bundle")
    sce_sys_dir = os.path.join(bundle_root, "sce_sys")
    data_dir = os.path.join(bundle_root, "data", "CUSA00419")

    # إعادة تهيئة مجلد التجميع النظيف بأمان
    if os.path.isfile(bundle_root):
        os.remove(bundle_root)
    if os.path.isdir(bundle_root):
        shutil.rmtree(bundle_root)

    os.makedirs(sce_sys_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    file_map = [
        ("assets/icon0.png", os.path.join(sce_sys_dir, "icon0.png")),
        ("assets/splash.png", os.path.join(sce_sys_dir, "pic1.png")),
        ("assets/ui.png", os.path.join(sce_sys_dir, "ui.png")),
        ("assets/ScorpionMenu-v1.2b-100US.prx", os.path.join(sce_sys_dir, "ScorpionMenu-v1.2b-100US.prx")),
        ("mod_data/CUSA00419/Blaze100_Theme.ini", os.path.join(sce_sys_dir, "Blaze100_Theme.ini")),
        ("mod_data/CUSA00419/Blaze100_Menu_AR.txt", os.path.join(sce_sys_dir, "Blaze100_Menu_AR.txt")),
        ("pkg_sce/param.json", os.path.join(sce_sys_dir, "param.json")),
        ("build_pkg/blaze100.gp4", os.path.join(bundle_root, "blaze100.gp4")),
        ("assets/ScorpionMenu-v1.2b-100US.prx", os.path.join(data_dir, "ScorpionMenu-v1.2b-100US.prx")),
        ("mod_data/CUSA00419/Blaze100_Theme.ini", os.path.join(data_dir, "Blaze100_Theme.ini")),
        ("mod_data/CUSA00419/Blaze100_Menu_AR.txt", os.path.join(data_dir, "Blaze100_Menu_AR.txt")),
    ]

    print("\n[PACKAGING FILES -> pkg_output/Blaze100_Bundle]")
    copied_count = 0
    for src, dst in file_map:
        if not os.path.isfile(src):
            print(f"  [ERROR] Missing source: {src}")
            sys.exit(1)
        shutil.copy2(src, dst)
        copied_count += 1
        print(f"  [COPIED] {src} -> {dst} ({os.path.getsize(dst)} bytes | sha256={sha256_file(dst)})")

    # إنشاء ملف بيان جاهزية البناء داخل الحزمة المجمّعة
    manifest_path = os.path.join(bundle_root, "BUILD_MANIFEST.txt")
    with open(manifest_path, "w", encoding="utf-8") as mf:
        mf.write("AppName: Blaze 100\n")
        mf.write("TargetGame: GTA V v1.00 (CUSA00419)\n")
        mf.write("Loader: GoldHEN\n")
        mf.write("ModFile: ScorpionMenu-v1.2b-100US.prx (2494752 bytes)\n")
        mf.write("ThemeFile: Blaze100_Theme.ini\n")
        mf.write("ArabicMenuFile: Blaze100_Menu_AR.txt\n")
        mf.write(f"PackagedEntries: {copied_count}\n")

    pkg_builder = shutil.which("orbis-pub-cmd")
    print("\n[PKG TOOL STATUS]")
    if pkg_builder:
        print(f"  - orbis-pub-cmd found at: {pkg_builder}")
    else:
        print("  - orbis-pub-cmd not installed in Termux; bundle staged cleanly in pkg_output/Blaze100_Bundle")

    print("\n====================================================")
    print("BUILD COMPLETE: pkg_output/Blaze100_Bundle IS READY")
    print("====================================================")

if __name__ == "__main__":
    main()
