# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['app.py'],
             pathex=['F:\\Usuarios\\aacevedo\\Entornos Virtuales\\Proyectos\\Proyectos DASH FLASK PLOTLY\\Flask'],
             binaries=[],
             datas=[],
             hiddenimports=['win32timezone','statsmodels.tsa.statespace._kalman_filter', 'statsmodels.tsa.statespace._kalman_smoother', 'statsmodels.tsa.statespace._representation', 'statsmodels.tsa.statespace._simulation_smoother', 'statsmodels.tsa.statespace._statespace', 'statsmodels.tsa.statespace._tools', 'statsmodels.tsa.statespace._filters._conventional', 'statsmodels.tsa.statespace._filters._inversions', 'statsmodels.tsa.statespace._filters._univariate', 'statsmodels.tsa.statespace._smoothers._alternative', 'statsmodels.tsa.statespace._smoothers._classical', 'statsmodels.tsa.statespace._smoothers._conventional', 'statsmodels.tsa.statespace._smoothers._univariate'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += [('favicon.ico','F:\\Usuarios\\aacevedo\\Entornos Virtuales\\Proyectos\\Proyectos DASH FLASK PLOTLY\\Flask\\assets\\favicon.ico','DATA')]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='pot',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
	  icon='F:\\Usuarios\\aacevedo\\Entornos Virtuales\\Proyectos\\Proyectos DASH FLASK PLOTLY\\Flask\\assets\\favicon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='app',
	       console=True)
