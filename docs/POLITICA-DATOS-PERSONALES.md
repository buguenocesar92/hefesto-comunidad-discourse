# Política de tratamiento de datos personales — Comunidad (Discourse) (Hefesto Studio)

Estado: vigente desde 2026-10-20. Responsable del tratamiento: el cliente que
opera el kit. Este documento describe qué datos guarda el kit, por qué, cuánto
tiempo los retiene y cómo se ejercen los derechos del titular (Ley 21.719).

## 1. Qué datos guarda este kit

El kit de comunidad (Discourse) guarda, por persona usuaria:

- **Cuenta del foro**: usuario, correo, avatar, fecha de registro,/ip de
  registro y preferencias.
- **Actividad**: publicaciones, respuestas, reacciones, temas seguidos, votes y
 bitácora de moderación.
- **Sesiones y correo**: cookies de sesión, tokens de recuperación de contraseña
  y el historial de correos enviados por el foro.
- **Reportes y moderación**: contenido reportado, decisiones del equipo de
  moderación y suspensiones y vetos.
- **Copias locales de respaldo**: `backups/<timestamp>/` con los datos del foro
  (`shared.tar.gz`), la configuración del contenedor (`app.yml`) y la
  configuración del kit.

Es el kit con más datos personales del grupo: la comunidad es un espacio
público con registro de personas identificables.

## 2. Qué datos NO guarda este kit

- El `.env` **no** se copia en claro al respaldo: solo sus nombres de variable
  (`env.vars`) y, si hay un receptor `age` configurado, el `.env` cifrado
  (`env.age`). Ver `docs/CONTRATO-RESPALDO.md`, regla 5.
- La imagen Docker del foro (`image.tar`) no se guarda por defecto: se reconstruye desde el registro y pesa gigabytes.

## 3. Base legal y deberes

- **Minimización**: el foro guarda lo que la conversación necesita (cuenta, correo, actividad). Los datos de personas que no participan no se contrastan con terceros ni se comparten.
- **Finalidad**: alojar la comunidad del cliente y moderarla. Los datos no se usan para otros fines ni se ceden a terceros.
- **Seguridad**: los respaldos se cifran en reposo hacia el destino del
  operador, la clave privada no está en este servidor y el `.env` nunca sale
  en claro.
- **Auditoría**: cada respaldo y cada restauración dejan registro en
  `logs/restore.log` con origen, sha256 verificado, destino y resultado. Es
  registro de actividades de tratamiento: no guarda valores de secretos.

## 4. Retención

| Dato | Dónde | Retención por defecto | Quién lo borra |
|---|---|---|---|
| Cuentas y perfil | PostgreSQL del foro (volumen `shared`) | mientras la cuenta exista | el operador, desde la interfaz |
| Publicaciones y respuestas | PostgreSQL del foro (volumen `shared`) | mientras el tema exista | el operador, desde la interfaz |
| Sesiones y tokens | PostgreSQL del foro (volumen `shared`) | hasta el cierre de sesión o su revocación | el operador |
| Correos enviados | buzón del servidor de correo | según la política de correo del cliente | el operador del correo |
| Moderación y auditoría | PostgreSQL del foro (volumen `shared`) | según la política del cliente | el operador |
| Respaldos en disco | `backups/<timestamp>/` | **a definir por el operador**; el kit no borra nada por su cuenta | el operador |
| Registro de auditoría | `logs/restore.log` | append-only; se trunca por política del cliente | el operador |

**El kit no borra respaldos ni datos por su cuenta.** Borrar es una decisión del
operador, porque un respaldo borrado no se recupera.

## 5. Derechos del titular (acceso, rectificación y supresión)

1. **Acceso**: entregar los datos de un titular concreto desde la interfaz del
   kit o desde el dump de la base.
2. **Rectificación**: corregir los datos desde la interfaz del kit.
3. **Supresión**: eliminar el registro y dejar constancia de la supresión en el
   registro de auditoría.
4. **Revocación del consentimiento**: si el tratamiento depende del
   consentimiento, eliminar el registro.

El kit garantiza que los datos son localizables, corregibles y borrables; el
cliente es quien conoce la identidad de los titulares.

## 6. Verificación

- `bats tests/backup_restore.bats` comprueba, con datos sintéticos, que el
  `.env` no queda en claro, que el manifiesto lleva las cinco claves, que un
  artefacto alterado se rechaza y que un destino no vacío aborta la
  restauración.
- `gitleaks` corre en CI sobre el repositorio y su historial.
