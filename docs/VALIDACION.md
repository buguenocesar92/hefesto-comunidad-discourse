# Validación · 2026-10-16
Realizado localmente:
- Sintaxis Python por AST y parseo YAML de la pasarela.
- .env se crea 0600 y rechaza sobrescritura sin alterar el original.
- Parser de entorno conserva valores literales con $/# y rechaza comillas, host con esquema, puerto SMTP no configurado y marcadores pendientes.
- La configuración generada es JSON/YAML válido, no contiene contraseña SMTP, no publica puertos y fija commit/base; añade etiqueta de propiedad del contenedor.
- Validador de archivo rechaza rutas absolutas, ../, symlinks y setuid.
- Mediante comandos simulados: respaldo de shared ficticio, captura de metadatos de imagen, hashes, rechazo de archivo alterado y reinicio tras fallo de copia de imagen. Solo se escribe completed para una copia terminada.
- Integridad ZIP; sin .env real, backups ni cachés.

No se ejecutó Docker, launcher, bootstrap, clonación de instalación, PostgreSQL, Redis, Rails, SMTP ni Caddy. La imagen guardada en la prueba era un archivo ficticio: no demuestra docker load ni restauración de datos reales. Tampoco se realizó prueba visual, de permisos en el foro, redes de Coolify o TLS.

Pendiente: docs/ACEPTACION.md completo en VPS de prueba, incluidos compatibilidad de base/commit, bootstrap y migraciones, entorno solo al iniciar, correo, proxy, cuenta administradora, permisos/categorías y recuperación física real en el mismo tipo de arquitectura. El manejo de tipos especiales en shared requiere comprobarse contra los datos reales del standalone.

No se publicó un foro, creó un usuario, envió correo ni activó una membresía/pago. Es un kit de despliegue preparado para probar.
