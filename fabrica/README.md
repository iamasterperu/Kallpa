# Fábrica de videos KALLPA (Instagram Reels)

Cada sábado se crean los 5 Reels de la semana siguiente (lunes, miércoles, viernes, sábado y domingo; 20 al mes) para **@kallpa_iamaster** y se programan en Metricool.

## Qué vendemos (no cambiar el enfoque)
KALLPA crea **apps web y software a medida para empresas, en 7 días o menos**: sistemas de pedidos, inventario, citas y reservas,
modernización de sistemas antiguos, catálogos, MVP de ideas, automatizaciones con IA, paneles de ventas, matrículas, etc.
Llave en mano: diseño, desarrollo con IA, pruebas al 100 %, capacitación y soporte. Precio cerrado después de una reunión gratis.
Público: dueños de pymes y empresas peruanas (clínicas, colegios, restaurantes, tiendas, ferreterías, constructoras, academias, hoteles…).
Nada de cursos, Full Day ni IAMASTER en estos videos. **No poner precios en soles de nuestros servicios.**

## Estilo de cada video
- 18 a 30 segundos, 4 a 6 escenas, voz en español (Daniela, animada) con subtítulos grandes y música.
- **Gancho fuerte en los primeros 2 segundos** (pregunta directa a un dolor, una cifra, "si tu empresa…", "deja de…").
- Problema → solución con la app → beneficio concreto → llamado a la acción.
- Siempre cerrar con la escena `cta`: el llamado principal es **"Agenda tu reunión GRATIS: toca el link de nuestro perfil"**; abajo, más pequeño, "o comenta PALABRA". La voz del cierre debe mandar al link del perfil.
- El caption también: línea "👉 Agenda tu reunión GRATIS en el link de nuestro perfil." y firstCommentText "👉 Agenda tu reunión gratis en el link de nuestro perfil @kallpa_iamaster 🚀".
- Lunes a viernes: problemas reales de empresas y la app que lo resuelve. Sábado y domingo: más ligeros o interactivos
  (juegos, "dime tu rubro", procesos, historias, antes/después).
- No repetir temas: revisa `historial.json`.

## Tipos de escena (campos)
| tipo | campos |
|---|---|
| gancho | etiqueta, titulo, emoji, sub |
| problema | titulo, items[3], contador (número), etiqueta |
| telefono | titulo, app, kpis[[etiqueta, valor] ×2], filas[3], sello |
| lista | titulo, items[[emoji, título, detalle] ×3-4] |
| antesdespues | titulo, antes[3], despues[3] |
| numero | titulo, numero, prefijo, sufijo, etiqueta |
| chips | titulo, emoji, chips[4-6] |
| chat | titulo, contacto, mensajes[["c" cliente / "k" app, texto] ×3] |
| cta | detalle (ej. "y te mostramos la demo") |

Todas llevan `voz` (lo que dice la voz; los números escritos en letras). En `titulo`, `sub` y `etiqueta` se puede usar
`<br>` y `<span class="y|g|r|v">` (amarillo, degradado, rojo, verde). Ejemplo completo: `semanas/2026-11-16.json`.
Cada video lleva además: archivo (`AAAA-MM-DD-palabra`, único: fecha de publicación + palabra, sin tildes ni espacios), dia, fecha, hora (Lima), tema, palabra, resaltar[], caption, hashtags[8].

## Pasos de cada sábado
1. `pip install piper-tts numpy` (si falta) · Playwright y ffmpeg ya vienen en el entorno.
2. Escribir `fabrica/semanas/<lunes>.json` con 5 videos nuevos: lunes, miércoles y viernes 19:00; sábado y domingo 11:00 (hora de Lima).
3. `python3 fabrica/fabrica.py fabrica/semanas/<lunes>.json /tmp/semana` (≈ 4 minutos) y revisar fotogramas de cada video.
4. `python3 fabrica/subir.py fabrica/semanas/<lunes>.json /tmp/semana` → URLs públicas en `https://kallpa.iamasterperu.workers.dev/v/…`.
5. En Metricool (marca con Instagram **kallpa_iamaster**), programar cada video como **REEL** en su fecha y hora,
   con `caption` + hashtags, `firstCommentText` invitando a comentar la palabra, `videoThumbnailUrl` = portada,
   e `isAiGenerated: true` (la voz es IA).
6. Agregar los temas a `historial.json`, hacer commit y push a `main`.
