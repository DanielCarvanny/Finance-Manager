# -*- mode: python ; coding: utf-8 -*-
# finance_manager.spec  –  PyInstaller 6.x  –  Python 3.13 / Windows

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# ---------------------------------------------------------------------------
# Caminhos base
# ---------------------------------------------------------------------------
BASE_DIR = os.path.abspath(SPECPATH)   # SPECPATH já é o diretório do .spec
VENV     = os.path.join(BASE_DIR, 'venv')
VENV_LIB = os.path.join(VENV, 'Lib', 'site-packages')

# ---------------------------------------------------------------------------
# DATAS  –  arquivos de dados que precisam ir junto com o executável
# ---------------------------------------------------------------------------
datas = [
    # Tema customizado da aplicação
    (os.path.join(BASE_DIR, 'src', 'ui', 'theme.json'), 'src/ui'),

    # Assets do CustomTkinter (imagens, temas internos)
    (os.path.join(VENV_LIB, 'customtkinter', 'assets'), 'customtkinter/assets'),
]

# Inclui todos os data-files reportados pelos hooks do customtkinter
datas += collect_data_files('customtkinter')

# ---------------------------------------------------------------------------
# BINARIES  –  DLLs extras (apenas as que o PyInstaller não detecta sozinho)
# ---------------------------------------------------------------------------
# NOTA: no PyInstaller 6.x com Python 3.13, os DLLs do Tcl/Tk vêm
# automaticamente da instalação do Python (não da venv).  Não precisamos
# listá-los manualmente — o hook do tkinter já cuida disso.
binaries = []

# Cryptography: o backend Rust (.pyd) às vezes não é detectado
_rust_pyd = os.path.join(VENV_LIB, 'cryptography', 'hazmat', 'bindings', '_rust.pyd')
if os.path.exists(_rust_pyd):
    binaries.append((_rust_pyd, '.'))

# ---------------------------------------------------------------------------
# HIDDEN IMPORTS  –  módulos que o PyInstaller não detecta via análise estática
# ---------------------------------------------------------------------------
hiddenimports = [
    # CustomTkinter e todos seus submódulos
    'customtkinter',
    *collect_submodules('customtkinter'),

    # Matplotlib – backend Tkinter
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends.backend_tkagg',
    'matplotlib.backends.backend_agg',

    # Pillow – helper para Tk
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageTk',

    # SQLAlchemy – dialeto SQLite
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.orm',

    # Criptografia
    'cryptography',
    'cryptography.fernet',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.backends',

    # Módulos internos da aplicação (lazy imports em runtime)
    'src.ui.app',
    'src.ui.components',
    'src.database.conexao',
    'src.database.seed',
    'src.models',
    'src.services',
    'src.utils.logger',
]

# ---------------------------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------------------------
a = Analysis(
    ['main.py'],
    pathex=[BASE_DIR, os.path.join(BASE_DIR, 'src')],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'test', 'tests'],
    noarchive=False,
)

# ---------------------------------------------------------------------------
# PYZ  –  arquivo comprimido com os módulos Python
# ---------------------------------------------------------------------------
pyz = PYZ(a.pure)

# ---------------------------------------------------------------------------
# EXE  –  executável final (one-folder mode)
# ---------------------------------------------------------------------------
exe = EXE(
    pyz,
    a.scripts,
    [],                                  # one-folder: sem binaries/datas aqui
    exclude_binaries=True,               # one-folder: binaries ficam na pasta
    name='FinanceManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                           # UPX pode corromper DLLs — desativado
    console=True,                        # True para debug; mude para False no release
    disable_windowed_traceback=False,
    icon=None,
)

# ---------------------------------------------------------------------------
# COLLECT  –  junta tudo na pasta dist/FinanceManager/
# ---------------------------------------------------------------------------
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='FinanceManager',
)