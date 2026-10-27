#!/usr/bin/env python3
"""Restauracion de hefesto-comunidad en un destino nuevo y vacio.

Sin --confirmar CONFIRMAR_RESTAURACION no se escribe nada; con --dry-run se
simula. Valida el manifiesto y los sha256 antes de tocar el destino, exige el
directorio de datos vacio y deja restore-report.json y auditoria.

El .env NO viaja en el respaldo: el destino debe conservar el suyo (SMTP,
sesiones). El respaldo solo deja los nombres de variable (env.vars) y, si hay
receptor age, el .env cifrado (env.age).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (ROOT, TARGET, check_source, cmd, root_only,  # noqa: E402
                    sha)
from respaldo_contrato import (RespaldoError, auditar, ejecutar,  # noqa: E402
                               ejecutar_check, escribir_informe, opciones_restore)

SOFTWARE = 'hefesto-comunidad'
VERSION = json.loads((ROOT / 'source-lock.json').read_text()).get(
    'discourse_version', '1.0.0')
DATABASE = 'postgresql'


def main():
    modo, origen = opciones_restore(sys.argv[1:])
    root_only()
    origen = Path(origen).resolve()
    ejecutar_check(str(origen), SOFTWARE, VERSION, DATABASE)
    if modo == 'dry-run':
        print('Simulacion: el respaldo es integro y no se escribio nada.')
        print('Para restaurar de verdad: --confirmar CONFIRMAR_RESTAURACION')
        return 0
    check_source()
    if subprocess.run(['docker', 'container', 'inspect', 'app'],
                      capture_output=True).returncode == 0:
        raise RespaldoError('Destino debe carecer del contenedor app; '
                            'no se destruye una instancia existente', 5)
    if not (TARGET / '.env').is_file():
        raise RespaldoError('Falta el .env del destino: el .env no viaja en el respaldo', 5)
    if not (TARGET / 'containers/app.yml').is_file() \
            or sha(TARGET / 'containers/app.yml') != sha(origen / 'app.yml'):
        raise RespaldoError('Conservar la configuracion del destino: app.yml', 5)
    shared = TARGET / 'shared/standalone'
    if shared.exists() and any(shared.iterdir()):
        raise RespaldoError('Destino de datos no vacio; no se sobrescribe', 5)
    meta = json.loads((origen / 'image.json').read_text())
    arch = cmd('docker', 'info', '--format={{.Architecture}}',
               capture_output=True, text=True).stdout.strip()
    aliases = {'x86_64': 'amd64', 'aarch64': 'arm64'}
    if aliases.get(arch, arch) != meta.get('Architecture') or meta.get('Os') != 'linux':
        raise RespaldoError('Arquitectura incompatible con copia fisica', 5)
    if (origen / 'image.tar').is_file():
        cmd('docker', 'image', 'load', '--input', str(origen / 'image.tar'))
        actual = json.loads(cmd('docker', 'image', 'inspect', meta['Id'],
                                capture_output=True, text=True).stdout)[0]
        if actual['Id'] != meta['Id']:
            raise RespaldoError('Imagen restaurada no coincide', 5)
        cmd('docker', 'image', 'tag', meta['Id'], 'local_discourse/app')
    shared.mkdir(parents=True, exist_ok=True)
    cmd('tar', '--numeric-owner', '-xzf', str(origen / 'shared.tar.gz'), '-C', str(shared))
    escribir_informe(origen, software=SOFTWARE, version=VERSION, database=DATABASE,
                     modo='confirmado', resultado='restaurado', destino=str(TARGET))
    auditar(ROOT, operacion='restore', kit=SOFTWARE, origen=str(origen),
            destino=str(TARGET), resultado='restaurado')
    print('Datos recuperados. No se ha iniciado el foro. Antes de arrancar: aislar '
          'salida y revisar correo, sesiones y trabajos pendientes.')
    return 0


if __name__ == '__main__':
    raise SystemExit(ejecutar(main))
