# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

ROOT = Path.cwd()
hiddenimports = collect_submodules("yt_dlp")


def collect_tree(folder_name: str):
    folder = ROOT / folder_name
    datas = []
    if not folder.exists():
        return datas
    for path in folder.rglob("*"):
        if path.is_file():
            relative_parent = path.relative_to(ROOT).parent
            datas.append((str(path), str(relative_parent)))
    return datas


datas = [
    (str(ROOT / "LICENSE"), "."),
    (str(ROOT / "README.md"), "."),
    (str(ROOT / "CHANGELOG.md"), "."),
    (str(ROOT / "PACKAGE_HISTORY.md"), "."),
]

datas += collect_tree("data")
datas += collect_tree("docs")
datas += collect_tree("locales")
datas += collect_tree("assets")

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VDM",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(ROOT / "assets" / "app_icon.ico"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="VDM",
)
