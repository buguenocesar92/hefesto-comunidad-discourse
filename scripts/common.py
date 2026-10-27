"""Utilidades propias del kit hefesto-comunidad (Discourse).

El contrato comun de respaldo vive en scripts/respaldo_contrato.py; aqui solo
queda lo especifico del kit (la instalacion de discourse vive fuera del
repositorio, en /var/discourse).
"""
import hashlib
import json
import os
import re
import subprocess
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / 'source-lock.json').read_text())
# La instalacion real vive fuera del repositorio. En la suite bats se puede
# apuntar a un arbol sintetico con DISCOURSE_TARGET.
TARGET = Path(os.environ.get('DISCOURSE_TARGET', '/var/discourse'))
EN_PRUEBA = os.environ.get('HEFESTO_KIT_TEST') == '1'


def cmd(*a, **kw):
    return subprocess.run(list(a), check=True, **kw)


def root_only():
    if EN_PRUEBA and not str(TARGET).startswith('/var/'):
        return
    if os.geteuid() != 0:
        raise SystemExit('Ejecutar con sudo en el VPS; opera /var/discourse')


def settings(path=None):
    values = {}
    for line in (path or ROOT / '.env').read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            raise SystemExit('Linea env invalida')
        k, v = line.split('=', 1)
        if not re.fullmatch(r'DISCOURSE_[A-Z_]+', k) or k in values:
            raise SystemExit('Clave env invalida/duplicada')
        if not v or v != v.strip() or '\x00' in v or v.startswith(('"', "'")):
            raise SystemExit('Valor env vacio o con comillas/espacios exteriores')
        values[k] = v
    required = ['DISCOURSE_HOSTNAME', 'DISCOURSE_DEVELOPER_EMAILS', 'DISCOURSE_SMTP_ADDRESS',
                'DISCOURSE_SMTP_PORT', 'DISCOURSE_SMTP_USER_NAME', 'DISCOURSE_SMTP_PASSWORD',
                'DISCOURSE_NOTIFICATION_EMAIL']
    if any(not values.get(k) or 'REEMPLAZAR' in values[k] for k in required):
        raise SystemExit('Completar dominio, administrador y SMTP')
    if not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?', values['DISCOURSE_HOSTNAME']) \
            or '.' not in values['DISCOURSE_HOSTNAME']:
        raise SystemExit('Usar hostname DNS sin esquema, ruta o puerto')
    if values['DISCOURSE_SMTP_PORT'] != '465' or values.get('DISCOURSE_SMTP_FORCE_TLS') != 'true' \
            or values.get('DISCOURSE_SMTP_OPENSSL_VERIFY_MODE') != 'peer':
        raise SystemExit('Este kit usa SMTP TLS implicito 465 con verificacion peer')
    for k in ['DISCOURSE_DEVELOPER_EMAILS', 'DISCOURSE_NOTIFICATION_EMAIL']:
        if any('@' not in x or x.endswith('.invalid') for x in values[k].split(',')):
            raise SystemExit('Correo invalido')
    return values


def config(values):
    return {'base_image': LOCK['base_image'],
            'templates': ['templates/postgres.template.yml', 'templates/redis.template.yml',
                          'templates/web.template.yml', 'templates/web.ratelimited.template.yml'],
            'expose': [],
            'labels': {'cl.hefesto.product': 'comunidad-discourse'},
            'params': {'version': LOCK['discourse_commit'],
                       'db_default_text_search_config': 'pg_catalog.spanish'},
            'env': {'LC_ALL': 'en_US.UTF-8', 'LANG': 'en_US.UTF-8',
                    'LANGUAGE': 'en_US.UTF-8', 'DISCOURSE_DEFAULT_LOCALE': 'es',
                    'DISCOURSE_HOSTNAME': values['DISCOURSE_HOSTNAME'],
                    'DISCOURSE_DEVELOPER_EMAILS': values['DISCOURSE_DEVELOPER_EMAILS']},
            'volumes': [{'volume': {'host': '/var/discourse/shared/standalone', 'guest': '/shared'}},
                         {'volume': {'host': '/var/discourse/shared/standalone/log/var-log',
                                     'guest': '/var/log'}}],
            'hooks': {}, 'run': []}


def check_source():
    if not (TARGET / 'launcher').is_file():
        raise SystemExit('Falta preparar /var/discourse')
    if EN_PRUEBA and not str(TARGET).startswith('/var/'):
        return
    rev = cmd('git', '-C', str(TARGET), 'rev-parse', 'HEAD',
              capture_output=True, text=True).stdout.strip()
    if rev != LOCK['launcher_commit']:
        raise SystemExit('Revision launcher distinta; revisar antes de operar')
    existing = subprocess.run(['docker', 'container', 'inspect', 'app'],
                              capture_output=True, text=True)
    if existing.returncode == 0:
        labels = json.loads(existing.stdout)[0].get('Config', {}).get('Labels') or {}
        if labels.get('cl.hefesto.product') != 'comunidad-discourse':
            raise SystemExit('El contenedor app pertenece a otra instalacion; no se opera')


def launch(action, with_env=False):
    args = [str(TARGET / 'launcher'), action, 'app']
    if with_env:
        args += ['--docker-args', '--env-file=/var/discourse/.env '
                 '--network=hefesto-comunidad --network-alias=discourse-native']
    return cmd(*args, cwd=TARGET)


def running():
    return cmd('docker', 'inspect', '--format={{.State.Running}}', 'app',
               capture_output=True, text=True).stdout.strip() == 'true'


def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def safe_tar(p):
    seen = set()
    total = 0
    with tarfile.open(p, 'r|gz') as tf:
        for m in tf:
            name = PurePosixPath(m.name)
            if name.is_absolute() or '..' in name.parts or not (m.isdir() or m.isfile()) \
                    or m.mode & 0o6000:
                raise SystemExit('Tar con ruta/tipo/modo no admitido')
            if str(name) in seen:
                raise SystemExit('Ruta tar duplicada')
            seen.add(str(name))
            total += m.size
            if len(seen) > 2000000 or total > 500 * 1024 ** 3:
                raise SystemExit('Tar demasiado grande para este kit')
