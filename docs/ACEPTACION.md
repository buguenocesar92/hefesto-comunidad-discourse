# Aceptación en VPS de prueba
- Revisiones de launcher/app y base coinciden con source-lock.json; bootstrap termina sin errores.
- El contenedor app no publica puertos de host; red/alias permiten solo la entrada prevista desde gateway. Coolify sirve el dominio por HTTPS.
- SMTP entrega correo real a un destinatario de prueba autorizado y valida TLS. Alta/activación, recuperación y notificaciones funcionan; comprobar que el administrador es el previsto.
- Revisar política de registro/login y permisos de categorías; probar privacidad desde visitante y cuentas de distintos grupos. Probar móvil, búsqueda, subida/lectura de un archivo ficticio y notificaciones.
- Confirmar cabeceras HTTPS, cookies, IP real/limitación sin confiar globalmente en proxies arbitrarios.
- Respaldar; comprobar hashes y ausencia de errores de tipos especiales en shared; reinicio tras copia correcto.
- Restaurar en otro host de la misma arquitectura, con salida aislada antes de iniciar; revisar usuarios, permisos, archivos y trabajos recuperados.
- Confirmar que no hay secretos SMTP en containers/app.yml ni en el historial Git; .env 0600. Revisar que la imagen guardada pertenece al contenedor respaldado.
- Definir responsables de moderación, retención, actualizaciones y recuperación antes de abrir a clientes.
