import ctypes
import os
import shutil
import subprocess
import sys
from pathlib import Path


APP_NAME = "MedInUse"
EXE_NAME = "MedInUse.exe"


def bundled_exe_path() -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / EXE_NAME


def install_dir() -> Path:
    root = os.getenv("LOCALAPPDATA") or str(Path.home())
    return Path(root) / "Programs" / APP_NAME


def desktop_dir() -> Path:
    return Path(os.path.join(os.path.expanduser("~"), "Desktop"))


def start_menu_dir() -> Path:
    root = os.getenv("APPDATA") or str(Path.home())
    return Path(root) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / APP_NAME


def create_shortcut(shortcut_path: Path, target_path: Path) -> None:
    shortcut = str(shortcut_path).replace("'", "''")
    target = str(target_path).replace("'", "''")
    working_dir = str(target_path.parent).replace("'", "''")
    shortcut_path.parent.mkdir(parents=True, exist_ok=True)
    command = (
        "$shell = New-Object -ComObject WScript.Shell; "
        f"$shortcut = $shell.CreateShortcut('{shortcut}'); "
        f"$shortcut.TargetPath = '{target}'; "
        f"$shortcut.WorkingDirectory = '{working_dir}'; "
        "$shortcut.Save()"
    )
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        check=True,
        startupinfo=startupinfo,
    )


def show_message(title: str, message: str) -> None:
    ctypes.windll.user32.MessageBoxW(None, message, title, 0x40)


def main() -> None:
    source = bundled_exe_path()
    if not source.exists():
        show_message("Instalação não concluída", f"Não encontrei o aplicativo principal: {source}")
        return

    target_dir = install_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / EXE_NAME
    shutil.copy2(source, target)

    create_shortcut(desktop_dir() / f"{APP_NAME}.lnk", target)
    create_shortcut(start_menu_dir() / f"{APP_NAME}.lnk", target)

    os.startfile(target)
    show_message("Instalação concluída", "O MedInUse foi instalado e os atalhos foram criados.")


if __name__ == "__main__":
    main()
