# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app\\controller\\Main.py'],
    pathex=[],
    binaries=[],
    datas=[('app/view/index.html', 'app/view'), ('app/view/App.html', 'app/view'), ('app/view/css/reset.css', 'app/view/css'), ('app/view/css/style.css', 'app/view/css'), ('app/view/css/log_style.css', 'app/view/css'), ('app/view/js/script.js', 'app/view/js'), ('app/Arquivos_Armazenados', 'app/Arquivos_Armazenados'), ('app/model/streamlit_app.py', 'app/model'), ('app/model/Side_Consult.py', 'app/model'), ('app/model/Users.py', 'app/model'), ('myenv', 'myenv')],
    hiddenimports=['pandas._libs.tslibs.timedeltas', 'pandas._libs.tslibs.timestamps', 'pandas._libs.tslibs.np_datetime', 'pandas._libs.tslibs.nattype', 'pandas._libs.tslibs.timezones', 'streamlit', 'flask'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
