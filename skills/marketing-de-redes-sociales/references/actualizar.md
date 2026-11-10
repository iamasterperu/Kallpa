# Cómo actualizar este skill

El skill vive en el repositorio `iamasterperu/Kallpa`, carpeta `skills/marketing-de-redes-sociales/`. Ahí se guarda cada versión con git.

## Qué cambiar y dónde
| Pedido | Archivo |
|---|---|
| Nuevos ganchos, fórmulas, ejemplos | references/ganchos.md |
| Otra forma de pedir la acción, captions, hashtags | references/llamadas-a-la-accion.md |
| Nuevo tipo de escena de video, otra voz, otra música | scripts/video.py + scripts/plantilla_video.css + references/videos.md |
| Nuevo tipo de slide, otro diseño de carrusel | scripts/carrusel.py + scripts/plantilla_carrusel.css + references/carruseles.md |
| Otra red, otro hosting, otra forma de programar | scripts/publicar.py + references/metricool.md |
| Un negocio nuevo o un cambio de marca | assets/marcas/<id>.json |
| Días y horas | calendario del perfil o references/calendario.md |

## Pasos
1. Haz el cambio.
2. Pruébalo con un ejemplo: `python3 scripts/video.py assets/ejemplos/videos-semana.json /tmp/t --solo 0 --marca kallpa` y/o `python3 scripts/carrusel.py assets/ejemplos/carruseles-semana.json /tmp/t --marca kallpa`, y mira las imágenes.
3. Anota el cambio en `VERSION.md` (versión, fecha y qué cambió).
4. Haz commit y push en el repo.
5. Vuelve a empaquetar el skill (`python -m scripts.package_skill <carpeta>` del skill-creator) y entrégale el `.skill` a la persona para que lo guarde en su cuenta, en claude.ai → Configuración → Capacidades → Skills. Así el cambio se usa en todas sus conversaciones.

Mantén el formato fijo: videos 9:16 (1080×1920) y carruseles 4:5 (1080×1350), salvo que la persona pida otro.
