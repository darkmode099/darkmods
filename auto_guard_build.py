import glob
import os
import shutil
import subprocess
import sys

def ensure_dirs():
    for d in ["assets", "src", "pkg_sce", "mod_data/CUSA00419", "build_pkg", "pkg_output"]:
        if os.path.isfile(d):
            raise RuntimeError(f"Path collision: '{d}' exists as a file instead of directory.")
        os.makedirs(d, exist_ok=True)
        os.chmod(d, 0o755)

def fix_csproj_lang_versions():
    patched = 0
    for csproj in glob.glob("**/*.csproj", recursive=True):
        try:
            content = open(csproj, "r", encoding="utf-8", errors="ignore").read()
            new_content = content
            for bad_ver in [
                "<LangVersion>7.3</LangVersion>",
                "<LangVersion>8.0</LangVersion>",
                "<LangVersion>9.0</LangVersion>",
                "<LangVersion>10.0</LangVersion>",
                "<LangVersion>latest</LangVersion>",
                "<LangVersion>Latest</LangVersion>",
            ]:
                new_content = new_content.replace(bad_ver, "<LangVersion>7.2</LangVersion>")
            if new_content != content:
                with open(csproj, "w", encoding="utf-8") as f:
                    f.write(new_content)
                patched += 1
                print(f"[FIX CS1617] Patched LangVersion -> 7.2 in {csproj}")
        except OSError:
            pass
    return patched

def check_tooling_status():
    tools = {
        "python3": shutil.which("python3"),
        "clang++": shutil.which("clang++"),
        "msbuild": shutil.which("msbuild"),
        "dotnet": shutil.which("dotnet"),
        "mono": shutil.which("mono"),
    }
    print("\n[TOOLING CHECK]")
    for name, path in tools.items():
        status = f"AVAILABLE ({path})" if path else "NOT FOUND (handled safely)"
        print(f"  - {name}: {status}")

def verify_core_inputs():
    required_files = [
        ("assets/icon0.png", 1),
        ("assets/splash.png", 1),
        ("assets/ui.png", 1),
        ("assets/ScorpionMenu-v1.2b-100US.prx", 2494752),
        ("pkg_sce/param.json", 10),
        ("src/main.cpp", 50),
        ("mod_data/CUSA00419/Blaze100_Theme.ini", 10),
        ("mod_data/CUSA00419/Blaze100_Menu_AR.txt", 10),
    ]
    problems = []
    for path, min_size in required_files:
        if not os.path.isfile(path):
            problems.append(f"MISSING FILE: {path}")
            continue
        sz = os.path.getsize(path)
        if min_size == 2494752 and sz != min_size:
            problems.append(f"PRX SIZE MISMATCH: {path} ({sz} != {min_size})")
        elif sz < min_size:
            problems.append(f"FILE TOO SMALL: {path} ({sz} bytes)")
    return problems

def regenerate_gp4():
    subprocess.run([sys.executable, "generate_gp4.py"], check=True)
    for gp4 in ["build_pkg/blaze100.gp4", "build_pkg/pkg_build.gp4"]:
        if not os.path.isfile(gp4) or os.path.getsize(gp4) == 0:
            raise RuntimeError(f"GP4 missing after generation: {gp4}")

def main():
    try:
        ensure_dirs()
        fix_csproj_lang_versions()
        check_tooling_status()

        problems = verify_core_inputs()
        if problems:
            print("\n[GUARD ERROR] Found input issues:")
            for p in problems:
                print("  -", p)
            sys.exit(1)

        regenerate_gp4()
        subprocess.run([sys.executable, "full_prebuild_check.py"], check=True)
        print("\n[GUARD OK] All errors from previous screenshots are guarded and verified.")
    except Exception as exc:
        print(f"\n[GUARD FAILED] {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()
