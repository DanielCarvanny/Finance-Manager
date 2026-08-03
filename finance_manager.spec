# finance_manager.spec
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('src')],          # Adiciona src/ ao path
    binaries=[],
    datas=[
        # Theme da interface
        ('src/ui/views/theme.json', 'ui/views'),
        # Scripts de migração do Alembic
        ('alembic', 'alembic'),
        ('alembic.ini', '.'),
        # Pasta completa src (para imports internos funcionarem)
        ('src', 'src'),
    ],
    hiddenimports=[
        'customtkinter',
        'matplotlib.backends.backend_tkagg',
        'sqlalchemy.dialects.sqlite',
        'alembic',
        'alembic.config',
        'alembic.command',
        'alembic.runtime.migration',
        'alembic.script',
        'cryptography.fernet',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FinanceManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # False = sem janela de terminal (app gráfico)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.ico',  # Descomente se tiver um ícone .ico
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FinanceManager',
)