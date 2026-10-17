#!/usr/bin/env python3
import json,os,shutil,sys
from common import ROOT,LOCK,TARGET,cmd,root_only,settings,config,check_source,launch
if len(sys.argv)!=2 or sys.argv[1] not in ['prepare','build','start','stop','rebuild']:raise SystemExit('Uso: sudo python3 scripts/manage.py prepare|build|start|stop|rebuild')
root_only();action=sys.argv[1]
if action=='prepare':
    values=settings();cmd('docker','info',stdout=__import__('subprocess').DEVNULL)
    if TARGET.exists():raise SystemExit('/var/discourse ya existe; no se sobrescribe ni adopta una instalacion ajena')
    if __import__('subprocess').run(['docker','container','inspect','app'],capture_output=True).returncode==0:raise SystemExit('Ya existe un contenedor app; no se adopta ni modifica')
    cmd('git','clone','https://github.com/discourse/discourse_docker.git',str(TARGET))
    cmd('git','-C',str(TARGET),'checkout','--detach',LOCK['launcher_commit'])
    (TARGET/'containers/app.yml').write_text(json.dumps(config(values),indent=2)+'\n');os.chmod(TARGET/'containers/app.yml',0o600)
    shutil.copy2(ROOT/'.env',TARGET/'.env');os.chmod(TARGET/'.env',0o600)
    result=__import__('subprocess').run(['docker','network','inspect',LOCK['network']],capture_output=True)
    if result.returncode:cmd('docker','network','create',LOCK['network'])
    else:
        n=json.loads(result.stdout)[0]
        if n.get('Driver')!='bridge' or n.get('Internal'):raise SystemExit('Red existente incompatible')
    print('Fuentes y configuracion preparadas. No se ha construido ni iniciado el foro.');raise SystemExit(0)
check_source()
if action in ['build','rebuild']:
    values=settings(TARGET/'.env');actual=json.loads((TARGET/'containers/app.yml').read_text())
    if actual!=config(values):raise SystemExit('app.yml no coincide con configuracion/lock. Revisar manualmente; no se sobrescribe')
    # Una reconstruccion migra datos: respaldar antes. No volver a iniciar automaticamente si falla.
    if action=='rebuild':launch('stop')
    elif __import__('subprocess').run(['docker','inspect','--format={{.State.Running}}','app'],capture_output=True,text=True).stdout.strip()=='true':raise SystemExit('Detener app antes de build; usar rebuild tras respaldo')
    launch('bootstrap')
    if action=='rebuild':launch('destroy');launch('start',True)
elif action=='start':
    settings(TARGET/'.env');launch('start',True)
elif action=='stop':launch('stop')
