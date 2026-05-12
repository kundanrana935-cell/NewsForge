# ============================================
# STARTUP SETUP
# Watcher aur Web App ko Windows startup mein add karta hai
# Ek baar chalao - phir automatic
# ============================================

import os
import sys
import subprocess
import winreg


def get_python_path():
    """Current Python executable path return karta hai."""
    return sys.executable


def get_project_path():
    """Project ka root path return karta hai."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_batch_file(name, script_path, batch_path):
    """Windows batch file banata hai hidden window ke saath."""
    python_exe = get_python_path()
    content = f"""@echo off
start /min "" "{python_exe}" "{script_path}"
"""
    with open(batch_path, "w") as f:
        f.write(content)
    print(f"✅ Batch file created: {batch_path}")


def add_to_startup(name, batch_path):
    """Windows Registry mein startup entry add karta hai."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, batch_path)
        winreg.CloseKey(key)
        print(f"✅ Startup mein add kiya: {name}")
        return True
    except Exception as e:
        print(f"❌ Startup add error: {e}")
        return False


def setup_startup():
    """Watcher aur Web App dono ko startup mein add karta hai."""
    project_path = get_project_path()

    # Batch files ka folder
    batch_folder = os.path.join(project_path, "startup")
    os.makedirs(batch_folder, exist_ok=True)

    # 1. Watcher startup
    watcher_script = os.path.join(project_path, "downloader", "watcher.py")
    watcher_batch = os.path.join(batch_folder, "start_watcher.bat")
    create_batch_file("NewsForge Watcher", watcher_script, watcher_batch)
    add_to_startup("NewsForgeWatcher", watcher_batch)

    # 2. Web App startup
    webapp_script = os.path.join(project_path, "webapp", "app.py")
    webapp_batch = os.path.join(batch_folder, "start_webapp.bat")
    create_batch_file("NewsForge WebApp", webapp_script, webapp_batch)
    add_to_startup("NewsForgeWebApp", webapp_batch)

    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("Laptop restart karo - sab automatically shuru ho jaayega.")
    print("\nWeb App: http://localhost:5000")
    print(f"Download folder: C:\\NewsVideos")
    print("=" * 50)


def remove_from_startup():
    """Startup entries remove karta hai."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        for name in ["NewsForgeWatcher", "NewsForgeWebApp"]:
            try:
                winreg.DeleteValue(key, name)
                print(f"✅ Removed: {name}")
            except FileNotFoundError:
                print(f"ℹ️  Not found: {name}")
        winreg.CloseKey(key)
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--remove":
        remove_from_startup()
    else:
        setup_startup()
