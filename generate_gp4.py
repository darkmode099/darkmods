import os

gp4_path = os.path.join("build_pkg", "blaze100.gp4")
compat_gp4 = os.path.join("build_pkg", "pkg_build.gp4")

entries = [
    ("sce_sys/icon0.png", "assets/icon0.png"),
    ("sce_sys/pic1.png", "assets/splash.png"),
    ("sce_sys/ui.png", "assets/ui.png"),
    ("sce_sys/ScorpionMenu-v1.2b-100US.prx", "assets/ScorpionMenu-v1.2b-100US.prx"),
    ("sce_sys/Blaze100_Theme.ini", "mod_data/CUSA00419/Blaze100_Theme.ini"),
    ("sce_sys/Blaze100_Menu_AR.txt", "mod_data/CUSA00419/Blaze100_Menu_AR.txt"),
]

lines = [
    '<?xml version="1.0" encoding="utf-8"?>',
    '<psproject fmt="gp4" version="1000">',
    '  <volume>',
    '    <volume_type>pkg_ps4_app</volume_type>',
    '    <package_content_id>UP9000-BLZ100001_00-BLAZE100APP00001</package_content_id>',
    '    <package_passcode>00000000000000000000000000000000</package_passcode>',
    '  </volume>',
    '  <files>',
]

missing = []
for target_name, src_rel in entries:
    if os.path.isfile(src_rel):
        lines.append(f'    <file orig_path="{src_rel}" targ_path="{target_name}"/>')
    else:
        missing.append(src_rel)

lines.extend([
    '  </files>',
    '</psproject>',
])

xml_content = "\n".join(lines) + "\n"
with open(gp4_path, "w", encoding="utf-8") as f:
    f.write(xml_content)
with open(compat_gp4, "w", encoding="utf-8") as f:
    f.write(xml_content)

print(f"GENERATED {gp4_path} ({os.path.getsize(gp4_path)} bytes)")
print(f"GENERATED {compat_gp4} ({os.path.getsize(compat_gp4)} bytes)")
if missing:
    print("WARNING MISSING FILES:", missing)
