#!/usr/bin/env python3
import json,sys
from common import ROOT,TARGET,cmd,root_only,check_source,verify,sha
if len(sys.argv)!=3 or sys.argv[2]!='--accept-restored-jobs':raise SystemExit('Uso: sudo python3 scripts/restore.py /ruta/respaldo --accept-restored-jobs')
root_only();p=verify(sys.argv[1]);check_source()
if __import__('subprocess').run(['docker','container','inspect','app'],capture_output=True).returncode==0:raise SystemExit('Destino debe carecer del contenedor app; no se destruye una instancia existente')
for src,dst in [('.env',TARGET/'.env'),('app.yml',TARGET/'containers/app.yml')]:
    if not dst.is_file() or sha(dst)!=sha(p/src):raise SystemExit('Conservar configuracion y secretos del respaldo: '+src)
shared=TARGET/'shared/standalone'
if shared.exists() and any(shared.iterdir()):raise SystemExit('Destino de datos no vacio; no se sobrescribe')
meta=json.loads((p/'image.json').read_text())
arch=cmd('docker','info','--format={{.Architecture}}',capture_output=True,text=True).stdout.strip()
aliases={'x86_64':'amd64','aarch64':'arm64'}
if aliases.get(arch,arch)!=meta['Architecture'] or meta['Os']!='linux':raise SystemExit('Arquitectura incompatible con copia fisica')
cmd('docker','image','load','--input',str(p/'image.tar'))
actual=json.loads(cmd('docker','image','inspect',meta['Id'],capture_output=True,text=True).stdout)[0]
if actual['Id']!=meta['Id']:raise SystemExit('Imagen restaurada no coincide')
cmd('docker','image','tag',meta['Id'],'local_discourse/app')
shared.mkdir(parents=True,exist_ok=True)
cmd('tar','--numeric-owner','-xzf',str(p/'shared.tar.gz'),'-C',str(shared))
print('Imagen y datos recuperados. No se ha iniciado el foro. Antes de arrancar: aislar salida y revisar correo, sesiones y trabajos pendientes.')
