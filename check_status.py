import hashlib
import os
import shutil

TARGET_PRX = "ScorpionMenu-v1.2b-100US.prx"
EXPECTED_PRX_SIZE = 2494752

def sha1_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

print("==========================================")
print("       BLAZE 100 - PROJECT STATUS REPORT")
print("==========================================")

# 1. فحص الصور الثلاث
print("\n[1] الصور الثلاث في assets/:")
for img_name in ["icon0.png", "splash.png", "ui.png"]:
    p = os.path.join("assets", img_name)
    if os.path.isfile(p) and os.path.getsize(p) > 0:
        print(f"  [OK] {p} -> {os.path.getsize(p)} bytes | sha1={sha1_file(p)[:10]}")
    else:
        print(f"  [MISSING] {p}")

# 2. فحص ملف ScorpionMenu-v1.2b-100US.prx
print(f"\n[2] ملف السكروبين ({TARGET_PRX}):")
prx_in_project = os.path.join("assets", TARGET_PRX)
found_prx = None

if os.path.isfile(prx_in_project):
    found_prx = prx_in_project
else:
    search_roots = [
        ".",
        os.path.expanduser("~"),
        "/sdcard",
        "/storage/emulated/0",
    ]
    skip_dirs = {"/Android/data", "/Android/obb", "/proc", "/sys", "/dev"}
    for base in search_roots:
        if not os.path.exists(base):
            continue
        for cur, dirs, files in os.walk(base, topdown=True):
            norm = cur.replace("\\", "/")
            if any(s in norm for s in skip_dirs):
                dirs[:] = []
                continue
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            if TARGET_PRX in files:
                cand = os.path.join(cur, TARGET_PRX)
                if os.path.isfile(cand):
                    found_prx = cand
                    break
        if found_prx:
            break

if found_prx:
    sz = os.path.getsize(found_prx)
    size_note = "EXACT MATCH (2,494,752 bytes)" if sz == EXPECTED_PRX_SIZE else f"SIZE DIFF (expected {EXPECTED_PRX_SIZE})"
    if os.path.abspath(found_prx) != os.path.abspath(prx_in_project):
        os.makedirs("assets", exist_ok=True)
        shutil.copy2(found_prx, prx_in_project)
        print(f"  [FOUND & COPIED] {found_prx} -> {prx_in_project}")
    else:
        print(f"  [FOUND] {prx_in_project}")
    print(f"  [SIZE] {sz} bytes ({size_note})")
else:
    print(f"  [NOT FOUND] {TARGET_PRX} غير موجود حالياً على الجهاز.")

# 3. فحص الأكواد والتهيئة (تحميل الصور + التأثيرات)
print("\n[3] فحص الأكواد والتأثيرات:")
main_cpp_path = os.path.join("src", "main.cpp")
param_json_path = os.path.join("pkg_sce", "param.json")

cpp_code = open(main_cpp_path, "r", encoding="utf-8", errors="ignore").read() if os.path.isfile(main_cpp_path) else ""
param_code = open(param_json_path, "r", encoding="utf-8", errors="ignore").read() if os.path.isfile(param_json_path) else ""

has_splash_param = ("startupImages" in param_code) and ("splash.png" in param_code)
has_hide_splash = "sceSystemServiceHideSplashScreen" in cpp_code
has_loading_fx = ("runFastLoadingBar" in cpp_code) and ("0, 20, 50, 80, 100" in cpp_code)
has_x_press_fx = ("ORBIS_PAD_BUTTON_CROSS" in cpp_code) and ("triggerButtonPressEffect" in cpp_code)
has_pad_init = ("scePadInit" in cpp_code) and ("scePadReadState" in cpp_code)

print(f"  - ربط شاشة التحميل في param.json: {'[OK]' if has_splash_param else '[MISSING]'}")
print(f"  - إخفاء شاشة التحميل بعد انتهائه: {'[OK]' if has_hide_splash else '[MISSING]'}")
print(f"  - تأثير شريط التحميل المتحرك (0% -> 100%): {'[OK]' if has_loading_fx else '[MISSING]'}")
print(f"  - قراءة اليد وتأثير ضغطة زر X: {'[OK]' if (has_pad_init and has_x_press_fx) else '[MISSING]'}")

print("\n==========================================")

# فحص ربط تثبيت ملف السكروبين ورسالة التفعيل عند ضغط زر X
cpp_latest = open("src/main.cpp", "r", encoding="utf-8", errors="ignore").read()
has_prx_install = ("installScorpionModToConsole" in cpp_latest) and ("ScorpionMenu-v1.2b-100US.prx" in cpp_latest) and ("CUSA00419" in cpp_latest)
has_notify_msg = ("sendConsoleActivationMessage" in cpp_latest) and ("Blaze 100 NOTIFICATION" in cpp_latest)
print(f"  - تثبيت ملف السكروبين تلقائياً عند ضغط X: {'[OK]' if has_prx_install else '[MISSING]'}")
print(f"  - رسالة وإشعار تفعيل المود عند التثبيت: {'[OK]' if has_notify_msg else '[MISSING]'}")
# فحص ملفات تخصيص المود في mod_data/CUSA00419
theme_ini = os.path.join("mod_data", "CUSA00419", "Blaze100_Theme.ini")
menu_ar = os.path.join("mod_data", "CUSA00419", "Blaze100_Menu_AR.txt")
has_theme = os.path.isfile(theme_ini) and ("Blaze 100" in open(theme_ini, "r", encoding="utf-8", errors="ignore").read())
has_menu_ar = os.path.isfile(menu_ar) and ("تعديل الأسلحة" in open(menu_ar, "r", encoding="utf-8", errors="ignore").read())
print(f"  - ملف ثيم وألوان Blaze 100 (بنفسجي/فضي): {'[OK]' if has_theme else '[MISSING]'}")
print(f"  - ملف القائمة العربية (Blaze100_Menu_AR.txt): {'[OK]' if has_menu_ar else '[MISSING]'}")
