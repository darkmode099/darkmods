import hashlib
import os

def sha1_short(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            b = f.read(65536)
            if not b:
                break
            h.update(b)
    return h.hexdigest()[:10]

def ok(flag):
    return "[OK]" if flag else "[MISSING]"

print("====================================================")
print("      BLAZE 100 - FULL PRE-BUILD VERIFICATION")
print("====================================================")

# 1. الصور الثلاث
imgs = ["icon0.png", "splash.png", "ui.png"]
img_hashes = {}
print("\n[1] الصور الثلاث (assets/):")
for name in imgs:
    p = os.path.join("assets", name)
    exists = os.path.isfile(p) and os.path.getsize(p) > 0
    if exists:
        h = sha1_short(p)
        img_hashes[name] = h
        print(f"  {ok(True)} {p} ({os.path.getsize(p)} bytes | sha1={h})")
    else:
        print(f"  {ok(False)} {p}")

all_unique_imgs = len(set(img_hashes.values())) == 3
print(f"  {ok(all_unique_imgs)} تميّز الصور الثلاث (كل صورة مستقلة ومختلفة)")

# 2. ملف ScorpionMenu-v1.2b-100US.prx
prx_path = os.path.join("assets", "ScorpionMenu-v1.2b-100US.prx")
prx_exists = os.path.isfile(prx_path)
prx_size = os.path.getsize(prx_path) if prx_exists else 0
print("\n[2] ملف السكروبين (ScorpionMenu-v1.2b-100US.prx):")
print(f"  {ok(prx_exists)} وجود الملف في assets/ScorpionMenu-v1.2b-100US.prx")
print(f"  {ok(prx_size == 2494752)} مطابقة الحجم ({prx_size} / 2494752 bytes)")

# 3. ملفات التخصيص والمود في mod_data/CUSA00419
theme_path = os.path.join("mod_data", "CUSA00419", "Blaze100_Theme.ini")
menu_ar_path = os.path.join("mod_data", "CUSA00419", "Blaze100_Menu_AR.txt")
theme_ok = os.path.isfile(theme_path) and ("#2B0A4A" in open(theme_path, encoding="utf-8", errors="ignore").read())
menu_ar_ok = os.path.isfile(menu_ar_path) and ("Blaze 100" in open(menu_ar_path, encoding="utf-8", errors="ignore").read())

print("\n[3] ملفات التخصيص والقائمة (mod_data/CUSA00419/):")
print(f"  {ok(theme_ok)} ملف الثيم والألوان (Blaze100_Theme.ini)")
print(f"  {ok(menu_ar_ok)} ملف القائمة العربية (Blaze100_Menu_AR.txt)")
print("  [INFO] شكل المود منيو داخل .prx ثنائي ولا يُعدَّل داخله مباشرة؛ التخصيص جاهز عبر ملفات المشروع.")

# 4. كود التطبيق والتهيئة (التحميل + تأثير X + التثبيت + الإشعار)
cpp_path = os.path.join("src", "main.cpp")
param_path = os.path.join("pkg_sce", "param.json")
cpp = open(cpp_path, encoding="utf-8", errors="ignore").read() if os.path.isfile(cpp_path) else ""
param = open(param_path, encoding="utf-8", errors="ignore").read() if os.path.isfile(param_path) else ""

loading_ok = ("runFastLoadingBar" in cpp) and ("0, 20, 50, 80, 100" in cpp) and ("sceSystemServiceHideSplashScreen" in cpp)
param_ok = ("startupImages" in param) and ("splash.png" in param) and ("Blaze 100" in param)
x_fx_ok = ("ORBIS_PAD_BUTTON_CROSS" in cpp) and ("triggerButtonPressEffect" in cpp)
install_ok = ("installScorpionModToConsole" in cpp) and ("CUSA00419" in cpp)
notify_ok = ("sendConsoleActivationMessage" in cpp) and ("Blaze 100 NOTIFICATION" in cpp)

print("\n[4] فحص كود التطبيق والتهيئة:")
print(f"  {ok(param_ok)} إعدادات التطبيق وشاشة البدء في pkg_sce/param.json")
print(f"  {ok(loading_ok)} التحميل السريع المتحرك (0% -> 100%) وإخفاء شاشة التحميل")
print(f"  {ok(x_fx_ok)} تأثير ضغطة زر X وقراءة أزرار اليد")
print(f"  {ok(install_ok)} تثبيت ملف السكروبين تلقائياً عند ضغط X")
print(f"  {ok(notify_ok)} رسالة وإشعار التفعيل عند التثبيت")

ready = all([
    len(img_hashes) == 3,
    all_unique_imgs,
    prx_exists,
    prx_size == 2494752,
    theme_ok,
    menu_ar_ok,
    param_ok,
    loading_ok,
    x_fx_ok,
    install_ok,
    notify_ok,
])

print("\n====================================================")
print("النتيجة النهائية: جاهز لتكوين التطبيق" if ready else "النتيجة النهائية: توجد نواقص تحتاج إكمال")
print("====================================================")
