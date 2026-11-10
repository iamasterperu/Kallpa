---
name: marketing-de-redes-sociales
description: Crea y programa contenido de redes sociales que vende, para cualquier negocio, en español. Produce Reels/TikToks verticales 9:16 con voz de IA, subtítulos y música, y carruseles 4:5, todos con gancho fuerte en los primeros segundos y una llamada a la acción clara; escribe descripciones y hashtags y los deja programados en Metricool por fecha y hora. Úsalo siempre que el usuario pida videos, reels, tiktoks, carruseles, posts, contenido para Instagram/TikTok/Facebook, un calendario de contenido, "los videos de la semana", publicaciones automáticas, ganchos, llamadas a la acción, captions o hashtags, o programar algo en Metricool, aunque no diga "skill" ni "marketing", y aunque sea para un negocio nuevo (KALLPA, IAMASTER o cualquier cliente).
---

# Marketing de redes sociales

Convierte la oferta de un negocio en contenido que la gente detiene, mira hasta el final y responde: **Reels/TikToks 9:16** y **carruseles 4:5**, programados en Metricool. Todo se genera con scripts de este skill, así que cada pieza sale con la misma calidad y la identidad de la marca.

Formatos fijos (no los cambies salvo que la persona lo pida):
- **Videos: vertical 9:16, 1080×1920**, 15 a 40 segundos.
- **Carruseles: 4:5, 1080×1350**, 5 a 8 slides.

## 1. Conoce la marca primero

Todo parte de un **perfil de marca** en `assets/marcas/<marca>.json` (nombre, inicial o logo, colores, usuario, público, oferta, llamada a la acción principal, tono, lo prohibido, datos de Metricool, hosting y calendario).
- Si la marca ya tiene perfil (hoy: `kallpa`, `iamaster`), léelo y respétalo: sobre todo `oferta`, `cta_principal` y `prohibido`.
- Si es un negocio nuevo, crea su perfil copiando `assets/marcas/_plantilla.json`. Lee `references/marcas.md` para saber qué preguntar y cómo inferir lo demás de su web o redes. Con nombre, rubro, colores y la llamada a la acción ya se puede empezar.

## 2. Planifica

- Revisa qué se publicó antes (historial del negocio, por ejemplo `fabrica/historial.json` en el repo de KALLPA) para **no repetir temas ni palabras clave**.
- Usa el calendario del perfil. Si no hay, propone el de `references/calendario.md` (5 videos por semana: lunes, miércoles y viernes 19:00; sábado y domingo 11:00; más 2 carruseles). Con el plan gratuito de Metricool cuenta las publicaciones del mes antes de programar.
- Un tema por pieza. Mezcla dolores reales del cliente, solución, prueba, proceso, mitos, comparaciones y contenido interactivo. Ideas en `references/calendario.md`.

## 3. Escribe el guion (aquí se gana o se pierde)

Lee `references/ganchos.md` y `references/llamadas-a-la-accion.md` antes de escribir. Lo esencial:
- **Gancho en los primeros 1 a 2 segundos**, en pantalla y en la voz: habla de un dolor concreto, una cifra, un error o una promesa. Nada de saludos ni de "en este video".
- **Estructura:** gancho → problema que duele → solución (el producto o servicio en acción) → beneficio concreto o prueba → **llamada a la acción única** que manda al link del perfil, al WhatsApp o a comentar una palabra.
- La voz dice los números en letras ("siete días"). Frases cortas, con energía, que se lean solas como subtítulo.
- Nada de inventar testimonios, cifras de clientes ni resultados garantizados. Si usas una cifra ilustrativa, márcala "(estimado)".

Formato de los planes JSON y tipos de escena:
- Videos → `references/videos.md` (escenas: gancho, problema, telefono, lista, antesdespues, numero, chips, chat, agenda, cta). Ejemplos: `assets/ejemplos/videos-semana.json` y `assets/ejemplos/video-presentacion-web.json`.
- Carruseles → `references/carruseles.md` (slides: portada, punto, lista, pasos, comparacion, dato, cita, cta). Ejemplo: `assets/ejemplos/carruseles-semana.json`.

Nombre de cada archivo: `AAAA-MM-DD-palabra` (fecha de publicación + palabra clave, sin tildes ni espacios). Así nunca se pisan dos archivos.

## 4. Genera

Requisitos: Python 3, `pip install piper-tts numpy pillow`, ffmpeg, Node con Playwright (vienen en el entorno de Claude Code en la nube). La voz (Piper, `es_AR-daniela-high`, ajustada para sonar animada) se descarga sola la primera vez.

```bash
S=<ruta de este skill>
python3 $S/scripts/video.py plan.json /tmp/salida --marca kallpa        # Reels 9:16 (≈30 s por video, 3 en paralelo)
python3 $S/scripts/carrusel.py plan.json /tmp/salida --marca kallpa     # Carruseles 4:5 + <archivo>-vista.jpg
```

Salidas: `<archivo>.mp4` + `<archivo>.jpg` (portada) + `.srt` por video; `<archivo>-01.jpg…` por carrusel.

**Revisa siempre antes de publicar.** Mira 3 o 4 fotogramas de cada video (`ffmpeg -ss <s> -i video.mp4 -frames:v 1 x.png`) y la `-vista.jpg` de cada carrusel. Busca textos cortados o tapados, emojis que no cargaron y que el gancho se lea a primera vista. Si algo falla, corrige el JSON (textos más cortos, menos ítems) y vuelve a generar solo esa pieza con `--solo N`. Muéstrale a la persona la vista previa (con SendUserFile o un enlace) antes de programar cuando sea la primera vez con esa marca o cuando lo pida.

## 5. Publica y programa en Metricool

Lee `references/metricool.md`. En resumen:
1. `python3 $S/scripts/publicar.py plan.json /tmp/salida --marca kallpa` sube los archivos al hosting de la marca y escribe `metricool.json` (una publicación por pieza) y `publicar.txt` (textos y links por si se publica a mano).
2. Comprueba la marca con `getBrandSettings` (el `blogId` y que la red esté conectada) y lo ya programado con `getScheduledPosts`, para no duplicar.
3. Por cada objeto de `metricool.json`, llama a `createScheduledPost` con su `date`, `blogId` e `info`. Si una publicación ya existe y hay que moverla, usa `updateScheduledPost` con el contenido completo.
4. Confirma con `getScheduledPosts` que todo quedó "PENDING". Guarda el historial (temas, palabras y links) y, si el contenido vive en un repo, haz commit.

Videos → Reel (`showReelOnFeed: true`, `isAiGenerated: true` por la voz de IA). Carruseles → POST con varias imágenes.

## 6. Entrega

Cierra con un resumen corto en español: tabla de día/hora, tema, gancho y palabra clave; dónde ver las piezas (Metricool → Planificador, la página de galería si existe, los links); y lo que falta que haga la persona (conectar una red, un permiso, etc.). Si no pudiste programar, dilo claramente y deja todo listo.

## Automatizar cada semana

Para que se haga solo (por ejemplo, cada sábado), crea una tarea programada que siga este skill. La plantilla del pedido y los requisitos (conector de Metricool, acceso al repo) están en `references/automatizar.md`.

## Mantener y mejorar este skill

Las reglas de estilo están en `references/`, los scripts en `scripts/`, las marcas en `assets/marcas/`. Cuando la persona pida un cambio ("más corto", "otra voz", "otro color", "nuevo tipo de slide"), aplícalo en el archivo correspondiente, prueba con un ejemplo y súbele la versión en `VERSION.md` (ver `references/actualizar.md`).
