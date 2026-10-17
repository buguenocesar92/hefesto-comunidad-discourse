# Copia fría y recuperación
## Crear
`sudo python3 scripts/backup.py`

Detiene app, comprueba parada, comprime shared con propietarios/permisos, guarda la imagen exacta usada por el contenedor, copia .env y app.yml y escribe un manifiesto con hashes y lock. Finalmente vuelve a iniciar el contenedor si antes estaba activo. Hay indisponibilidad durante toda la copia; no reconstruir ni desplegar a la vez.

El script rechaza enlaces, sockets/dispositivos y modos especiales en shared en lugar de omitirlos silenciosamente. Si la instalación incorpora enlaces/tablespaces externos o quedan sockets tras parar, investigar y adoptar una copia adecuada antes de marcarla como válida. Esta ruta está preparada para el standalone sin personalizaciones de almacenamiento.

`python3 scripts/check_backup.py /ruta/respaldo` valida hashes y rutas. Límite: 2 millones de entradas y 500 GiB expandidos para shared. Los hashes detectan corrupción, no autenticidad: usar únicamente copias de confianza. image.tar se carga con Docker y contiene código ejecutable.

Incluye DB, Redis, usuarios, mensajes, archivos locales, sesiones/colas, secretos y logs de shared, además de la imagen. No incluye DNS/TLS/Coolify/firewall, S3 externo, ni garantiza que se pueda operar sin Internet: preparar el launcher y su imagen auxiliar puede requerir descargar fuentes/base. Archivar esos componentes por separado si se necesita recuperación totalmente offline.

## Recuperar en otro host
1. Usar Linux con la misma arquitectura y este kit/lock. No instalar encima de otro /var/discourse ni reutilizar un contenedor app existente. No se cambian nombres automáticamente.
2. Copiar privadamente .env del respaldo a la carpeta del kit, 0600. No generar contraseñas nuevas. Ejecutar manage.py prepare para clonar el launcher y crear app.yml/red; no hacer build ni start. Debe coincidir exactamente con app.yml del respaldo. No cambiar dominio/secretos durante la recuperación inicial.
3. Verificar el respaldo. Ejecutar `sudo python3 scripts/restore.py /ruta/respaldo --accept-restored-jobs`. Comprueba que app no existe, shared está vacío, .env/config coinciden y la arquitectura es compatible. Carga la imagen guardada, la etiqueta local_discourse/app y extrae datos con propietarios numéricos. No inicia el foro ni borra nada existente. Si falla parcialmente, investigar y repetir en un destino nuevo.
4. Antes de arrancar un ensayo, aislar su salida a Internet y el acceso de usuarios, manteniendo el sistema original fuera de esa prueba. El respaldo puede reactivar correo pendiente, resúmenes, trabajos y sesiones. La red normal de este kit **no bloquea** salida: la restricción del host para un ensayo debe prepararse y comprobarse aparte. No afirmar que un ensayo es inocuo solo porque no está en DNS público.
5. Iniciar mediante manage.py start cuando el aislamiento esté comprobado; probar login, permisos, lectura, publicación ficticia, búsqueda y archivos. No conectar a clientes reales hasta revisar trabajos/correo y acordar el corte del original.

Esta copia física sirve para recuperar la misma imagen/datos, no para migrar directamente a Supabase ni entre versiones mayores de PostgreSQL. Conservar también backups nativos de Discourse con uploads según las instrucciones de la versión instalada; no se automatiza aquí su restauración lógica.
