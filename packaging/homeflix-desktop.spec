# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the release packages: Windows (single .exe), macOS (Lumbuz.app) and Linux (folder).
# Build from the repository root after `python packaging/make_icon.py`:
#   pyinstaller --noconfirm packaging/homeflix-desktop.spec
# The personal data/ folder is not bundled: packaged builds keep their library in the user's data folder.
import os
import sys

ROOT = os.path.abspath(os.path.join(SPECPATH, '..'))
ICONS = os.path.join(ROOT, 'build', 'icons')
VERSION = os.environ.get('HOMEFLIX_VERSION', '2.0.0').lstrip('v')

a = Analysis(
    [os.path.join(ROOT, 'app.py')],
    pathex=[ROOT],
    datas=[(os.path.join(ROOT, 'templates'), 'templates'), (os.path.join(ROOT, 'static'), 'static')]
    + ([(os.path.join(ROOT, 'VERSION'), '.')] if os.path.exists(os.path.join(ROOT, 'VERSION')) else []),
    hiddenimports=['waitress', 'webview'],
    excludes=['matplotlib', 'numpy', 'pandas', 'tkinter'],
    noarchive=False,
)
pyz = PYZ(a.pure)

if sys.platform == 'win32':
    exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='Lumbuz', console=True, upx=False,
              icon=os.path.join(ICONS, 'lumbuz.ico'))
else:
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='Lumbuz', console=sys.platform != 'darwin',
              upx=False, icon=os.path.join(ICONS, 'lumbuz.png'))
    coll = COLLECT(exe, a.binaries, a.datas, upx=False, name='Lumbuz')
    if sys.platform == 'darwin':
        app = BUNDLE(
            coll,
            name='Lumbuz.app',
            icon=os.path.join(ICONS, 'lumbuz.png'),
            bundle_identifier='com.kaptanoguz.homeflix',
            version=VERSION,
            info_plist={
                'CFBundleDisplayName': 'Lumbuz',
                'CFBundleShortVersionString': VERSION,
                'NSHighResolutionCapable': True,
                'LSApplicationCategoryType': 'public.app-category.entertainment',
                # The player loads posters and video over the home network (plain http).
                'NSAppTransportSecurity': {'NSAllowsArbitraryLoads': True},
                'NSLocalNetworkUsageDescription': 'Lumbuz ev ağındaki cihazlara film ve dizi sunar.',
            },
        )
