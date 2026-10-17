# Fuentes · 2026-10-16
- https://github.com/discourse/discourse_docker
- https://github.com/discourse/discourse_docker/blob/main/launcher
- https://github.com/discourse/discourse_docker/blob/main/samples/standalone.yml
- https://github.com/discourse/discourse_docker/blob/main/templates/web.template.yml
- https://github.com/discourse/discourse/blob/stable/lib/version.rb
- https://github.com/discourse/discourse/blob/main/docs/INSTALL-cloud.md
- https://hub.docker.com/r/discourse/base
- https://meta.discourse.org/

Los commits efectivos y digest están registrados en source-lock.json. Las ramas de las URLs son mutables; el kit prepara las fuentes mediante checkout del commit. Se conserva muestra/README upstream. app.yml generado es JSON válido como YAML, aceptado por el parser YAML del launcher. No se modifica el motor de Discourse; se omite el plugin opcional docker_manager y se utiliza la administración CLI.
