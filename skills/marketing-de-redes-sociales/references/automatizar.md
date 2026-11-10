# Automatizar cada semana

Una tarea programada (create_trigger, con `create_new_session_on_fire: true`) puede correr este skill cada semana, por ejemplo el sábado a las 7:37 (hora de Lima), y dejar programada la semana siguiente.

## Requisitos de la tarea
- **Conector de Metricool** activo en la tarea (en claude.ai → Tareas programadas → editar → conectores). Si se crea desde una sesión sin conectores, hay que activarlo a mano ahí.
- **Repositorio** donde vive el historial (y este skill) con acceso para push, por ejemplo `iamasterperu/Kallpa`.
- **Cloudflare** en el entorno si el hosting es `cloudflare_kv`.

## Pedido base (adaptar marca, días y horas)
```
Usa el skill marketing-de-redes-sociales con la marca <id>. Hoy es sábado: deja listos y programados en Metricool
los Reels 9:16 (y carruseles 4:5 si el perfil los incluye) de la SEMANA SIGUIENTE según el calendario del perfil.
1) Agrega el repo <owner/repo> con add_repo (push), lee el historial y no repitas temas ni palabras.
2) Si ya hay publicaciones para esas fechas en el historial o en Metricool, no crees nada nuevo: solo verifica.
3) Escribe los planes, genera con scripts/video.py y scripts/carrusel.py, revisa fotogramas, sube y arma
   metricool.json con scripts/publicar.py, y programa cada pieza con createScheduledPost.
4) Actualiza el historial (y la galería si existe), haz commit y push.
5) Termina con un resumen corto en español: días, horas, temas, links y si quedó todo programado o qué falta.
No hagas preguntas: decide tú.
```

## KALLPA (ya configurado)
Existe la tarea "Reels semanales KALLPA" (sábados 7:37, Lima) con el calendario lunes, miércoles y viernes 19:00, y sábado y domingo 11:00. Usa la fábrica del repo (`fabrica/`), que es la misma de este skill.
