#!/usr/bin/env python3
"""Respaldo del kit hefesto-comunidad (Discourse).

El .env nunca se copia en claro: al respaldo solo van sus nombres (env.vars) y,
si hay receptor age, el .env cifrado (env.age). El manifiesto lleva las cinco
claves del contrato. Ver docs/CONTRATO-RESPALDO.md.

La imagen Docker del foro (image.tar, varios gigabytes y reconstruible desde el
registro) NO se guarda por defecto: se incluye solo con --con-imagen.
"""
import datetime
import json
import os
import shutil
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (LOCK, ROOT, TARGET, check_source, cmd, root_only,  # noqa: E402
                    running, safe_tar)
from respaldo_contrato import (escribir_manifiesto, ejecutar,  # noqa: E402
                               exportar_env, marcar_fallido)

SOFTWARE = 'hefesto-comunidad'
VERSION = str(LOCK.get('discourse_version') or LOCK.get('discourse_commit') or '1.0.0')
DATABASE = 'postgresql'


def main():
    root_only()
    check_source()
    os.umask(0o077)
    con_imagen = '--con-imagen' in sys.argv[1:]
    shared = TARGET / 'shared/standalone'
    if not shared.is_dir():
        raise SystemExit('No hay datos del foro')
    image = cmd('docker', 'inspect', '--format={{.Image}}', 'app',
                capture_output=True, text=True).stdout.strip()
    meta = json.loads(cmd('docker', 'image', 'inspect', image,
                          capture_output=True, text=True).stdout)[0]
    p = ROOT / 'backups' / datetime.datetime.now(datetime.timezone.utc).strftime(
        '%Y%m%dT%H%M%S%fZ')
    p.mkdir(parents=True, mode=0o700)
    was_running = running()

    def filter_member(m):
        if not (m.isdir() or m.isfile()) or m.mode & 0o6000:
            raise SystemExit('Dato no regular/enlace o modo especial en shared; '
                             'revisar antes de respaldar')
        return m

    try:
        cmd(str(TARGET / 'launcher'), 'stop', 'app', cwd=TARGET)
        if running():
            raise SystemExit('app sigue activo; no se respalda')
        with tarfile.open(p / 'shared.tar.gz', 'w:gz') as tf:
            tf.add(shared, arcname='.', filter=filter_member)
        safe_tar(p / 'shared.tar.gz')
        (p / 'image.json').write_text(json.dumps(
            {k: meta[k] for k in ['Id', 'Architecture', 'Os'] if k in meta}, indent=2))
        if con_imagen:
            with (p / 'image.tar').open('wb') as f:
                cmd('docker', 'image', 'save', image, stdout=f)
        shutil.copy2(TARGET / 'containers/app.yml', p / 'app.yml')
        shutil.copy2(ROOT / 'source-lock.json', p / 'source-lock.json')
        meta_env = exportar_env(TARGET, p)
        escribir_manifiesto(p, SOFTWARE, VERSION, DATABASE, extra=meta_env)
    except BaseException:
        marcar_fallido(p, SOFTWARE, VERSION, DATABASE)
        raise
    finally:
        if was_running:
            cmd(str(TARGET / 'launcher'), 'start', 'app', cwd=TARGET)
    print('Respaldo completado:', p)
    print('El .env no viaja en claro: solo env.vars y, si hay receptor age, env.age.')
    if not con_imagen:
        print('La imagen del foro no se incluyo (--con-imagen para incluirla).')
    return 0


if __name__ == '__main__':
    raise SystemExit(ejecutar(main))
