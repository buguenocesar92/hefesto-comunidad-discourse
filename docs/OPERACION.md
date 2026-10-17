# Operación
## Responsabilidades
Launcher administra el contenedor app y /var/discourse/shared/standalone. Coolify administra únicamente la pasarela. No intentar que Coolify reconstruya/distribuya la imagen del foro como si fuera una imagen genérica sin los templates y datos oficiales. Solo una instancia con estos nombres por host en este kit.

Para acceso de mantenimiento: `cd /var/discourse` y `sudo ./launcher enter app`. No copiar diagnósticos que contengan emails, tokens o secretos a servicios públicos. Revisar logs de app, espacio, tareas, backups y fallos SMTP. Probar entrega real del proveedor antes de abrir registros/invitaciones.

## Cambios de SMTP
Editar /var/discourse/.env conservando permisos 0600 y copia segura. Respaldar primero. `sudo python3 scripts/manage.py rebuild` detiene app, hace bootstrap sin SMTP, destruye solo el contenedor anterior y crea el nuevo con entorno/red; no borra shared. Si falla bootstrap, deja el foro detenido para investigar: no se vuelve a una versión anterior automáticamente porque pudo haber migraciones.

No usar launcher rebuild/start sin el wrapper cuando se pretende conservar el paso de env-file/red. Un docker restart de un contenedor existente conserva su entorno, pero no lee cambios del archivo. No publicar imágenes debug de bootstrap o imágenes operativas sin revisar su contenido.

## Actualización
El lock captura stable al 16-10-2026. Para actualizar hay que seleccionar una revisión soportada, revisar cambios del launcher/templates/base y plugins, construir/ensayar en otra instalación y renovar lock/config de forma coherente. No cambiar la versión mayor de PostgreSQL ni restaurar datos físicos en otra arquitectura mediante ensayo y error. La vía nativa de backup lógico/restauración de Discourse es la alternativa para migraciones soportadas; confirmar instrucciones upstream de las versiones exactas.

## Proxy y acceso
La pasarela no incorpora Basic Auth: la identidad, sesión y permisos son de Discourse. Verificar que se ven HTTPS, cookies/origen correctos, uploads y canal de notificaciones/message bus. Revisar IP real y límites de petición con el proxy: no declarar como confiables todos los rangos de Internet para resolver un problema de cabeceras. El kit no modifica la configuración de Cloudflare ni valida reglas externas.

No configurar un check de salud que trate como error una redirección legítima a login en una comunidad privada. Validar el flujo esperado tras configurar el acceso.
