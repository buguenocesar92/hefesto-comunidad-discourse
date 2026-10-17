# Hefesto Comunidad · Discourse 2026.7.3
Kit para un foro de clientes, soporte comunitario, documentación conversada y comunidad privada. Utiliza Discourse nativo con su launcher oficial; no es un Compose alternativo que reemplace el instalador. La interfaz y funciones son las de Discourse, con configuración inicial en español.

## Stack y alcance
- Discourse stable 2026.7.3 fijado al commit de source-lock.json.
- discourse_docker fijado a un commit; base de construcción fijada por digest.
- PostgreSQL, Redis, servidor web y trabajos en el contenedor standalone oficial.
- Caddy como pasarela a Coolify: solo Coolify administra esa pasarela. El foro se administra mediante launcher y los scripts de este kit.
- Configuración SMTP en .env, copia fría de datos + imagen construida, verificación y restauración en destino nuevo.
- Guías de categorías, moderación, membresías y conexión con WordPress/Odoo.

No usa Supabase: esta entrega conserva los datos nativos del standalone. No hay pagos, suscripciones automáticas ni cuentas de usuarios reales creadas. El ZIP tampoco contiene Docker, imágenes, gemas ni los datos del foro.

## Requisitos
Linux de 64 bits, Docker Engine instalado y operativo, Git, Python 3.11+, GNU tar, dominio propio y SMTP con TLS implícito 465. Como presupuesto inicial de prueba, reservar 2–4 CPU, 4 GB RAM y disco libre para la compilación y dos copias completas de datos/imagen; medir para el tamaño real de la comunidad. Mantener respaldo fuera del VPS.

El kit ocupa /var/discourse, el nombre de contenedor app y la red hefesto-comunidad. No usarlo encima de un Discourse existente. En un VPS con varios servicios revisar esos nombres y recursos antes de preparar; el script rechaza un /var/discourse existente. No instala Docker ni cambia firewall, DNS o servicios ajenos.

## Configurar y preparar
1. Descomprimir en una carpeta de administración privada, fuera de /var/discourse. Ejecutar `python3 scripts/configure.py`.
2. Editar .env: dominio DNS sin https, email del administrador previsto, dirección SMTP, usuario, contraseña y remitente. Usar formato literal Docker env-file: sin comillas, export o interpolación. Un $ dentro de la contraseña es literal. No colocar saltos de línea ni espacios exteriores. El archivo queda 0600 y no debe entrar a Git.
3. Ejecutar `sudo python3 scripts/manage.py prepare`. Clona las fuentes oficiales en /var/discourse, selecciona el commit fijado, copia la .env con 0600, genera containers/app.yml sin contraseña SMTP y crea la red si hace falta. No construye ni inicia el foro.
4. Ejecutar `sudo python3 scripts/manage.py build`. Construye con launcher bootstrap y los templates oficiales. El bootstrap no recibe el archivo de secretos SMTP. Puede descargar paquetes/gemas y tardar; commits y base fijados no hacen una construcción completamente hermética.
5. Ejecutar `sudo python3 scripts/manage.py start`. Pasa /var/discourse/.env por --env-file solo al inicio y conecta el contenedor a la red con alias discourse-native. No publica puertos de host. La configuración activa de SMTP a partir de aquí está en /var/discourse/.env; la .env del kit es la copia inicial.

Discourse genera otros secretos propios en su entorno de datos: conservar shared completo y la imagen como indica la guía de respaldo. Docker y los administradores del host pueden leer variables de ejecución; env-file evita versionar la contraseña y ponerla en YAML, no la oculta al administrador.

## Conectar con Coolify
En el **mismo VPS/Docker Engine**, importar este kit o un repositorio privado con compose.gateway.yaml y ops/Caddyfile como recurso Docker Compose de Coolify. Seleccionar compose.gateway.yaml y asignar el dominio HTTPS del foro al servicio gateway, puerto 8080. La red externa hefesto-comunidad ya debe existir por prepare. El recurso no necesita la .env SMTP ni credenciales del foro: no las pegar en Coolify para este proxy.

TLS termina en Coolify. Caddy reenvía a discourse-native:80 y fija X-Forwarded-Proto=https; esta pasarela es exclusivamente para entrada HTTPS mediante el proxy, no un servidor HTTP público autónomo. No publicar puertos de gateway ni exponer app/PostgreSQL/Redis. No añadir SSL/Let's Encrypt dentro del template de Discourse en esta configuración: TLS se gestiona en el proxy exterior.

Mantener dominio y administración bajo control del operador mientras se hace el primer alta. Crear la cuenta con el email incluido en DISCOURSE_DEVELOPER_EMAILS, comprobar que recibe el correo de activación y confirmar acceso de administrador. Completar el asistente de instalación. Antes de abrir la comunidad: revisar políticas de registro, acceso privado y permisos de categorías según docs/COMUNIDAD.md. El kit no afirma que la primera pantalla sea ya una comunidad cerrada.

Si Coolify está en otro servidor, esta red Docker no se comparte: se necesita otro diseño de conectividad/proxy. No publicar la base para resolverlo. Ver docs/OPERACION.md.

## Operación
Usar `sudo python3 scripts/manage.py stop|start`. Para actualizar/reconstruir: respaldo primero, revisión de versión/templates, `sudo python3 scripts/manage.py rebuild`. El kit no actualiza automáticamente el lock ni hace git pull. No se añade el plugin docker_manager; por tanto no se promete actualización mediante el panel.

El inicio reutiliza un contenedor existente; cambiar .env no actualiza su entorno automáticamente. Recrear/reconstruir tras respaldar siguiendo docs/OPERACION.md. No usar launcher rebuild directamente sin comprender que este kit añade --env-file y red solo en start.

El respaldo físico conserva imagen y datos juntos. Ver docs/RESPALDO.md. Los archivos contienen datos personales y secretos, no deben subirse a repositorios públicos.

## Traspaso y comercialización
Ofrecer instalación, estructura de categorías, moderación, soporte y mantenimiento. Las membresías de pago necesitan una pasarela y una integración adicional; en esta entrega se proponen niveles/grupos manuales sin ejecutar cobros. Discourse tiene licencia GPL; conservar atribuciones y revisar licencias de plugins que se añadan. No se ha conectado OAuth, Odoo, WordPress o pagos: docs/INTEGRACIONES.md explica el alcance.

Revisado localmente, sin Docker ni instalación real ejecutada. Completar docs/ACEPTACION.md antes de atender clientes.
