#!/usr/bin/env python3
import datetime,json,os,shutil,stat,tarfile
from common import ROOT,LOCK,TARGET,cmd,root_only,check_source,running,launch,sha,safe_tar
root_only();check_source();os.umask(0o077)
shared=TARGET/'shared/standalone'
if not shared.is_dir():raise SystemExit('No hay datos del foro')
image=cmd('docker','inspect','--format={{.Image}}','app',capture_output=True,text=True).stdout.strip()
meta=json.loads(cmd('docker','image','inspect',image,capture_output=True,text=True).stdout)[0]
p=ROOT/'backups'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');p.mkdir(parents=True,mode=0o700)
was_running=running()
def filter_member(m):
    if not(m.isdir() or m.isfile()) or m.mode&0o6000:raise SystemExit('Dato no regular/enlace o modo especial en shared; revisar antes de respaldar')
    return m
try:
    launch('stop')
    if running():raise SystemExit('app sigue activo; no se respalda')
    # Sockets ya no deben existir despues de un cierre limpio; no se omiten silenciosamente datos.
    with tarfile.open(p/'shared.tar.gz','w:gz') as tf:tf.add(shared,arcname='.',filter=filter_member)
    safe_tar(p/'shared.tar.gz')
    with (p/'image.tar').open('wb') as f:cmd('docker','image','save',image,stdout=f)
    (p/'image.json').write_text(json.dumps({k:meta[k] for k in ['Id','Architecture','Os']},indent=2))
    shutil.copy2(TARGET/'.env',p/'.env');shutil.copy2(TARGET/'containers/app.yml',p/'app.yml');shutil.copy2(ROOT/'source-lock.json',p/'source-lock.json')
    files=['shared.tar.gz','image.tar','image.json','.env','app.yml','source-lock.json']
    (p/'manifest.json').write_text(json.dumps({'product':'hefesto-comunidad','status':'completed','lock':LOCK,'sha256':{n:sha(p/n) for n in files}},indent=2))
    print('Respaldo frio con imagen:',p,'Contiene datos, sesiones y secretos; cifrar fuera del VPS.')
finally:
    if was_running:launch('start',True)
