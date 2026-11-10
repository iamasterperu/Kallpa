# Carruseles 4:5 (1080×1350)

`scripts/carrusel.py` crea cada slide como JPG de 1080×1350 con la identidad de la marca: logo y @usuario arriba, puntos de progreso y "Desliza →" abajo, contador "2/6", y una línea de color que continúa de un slide al siguiente para que se sienta como un solo carrusel. También genera `<archivo>-vista.jpg` con todos los slides en fila para revisarlos de un vistazo. Tema `oscuro` o `claro` según el perfil.

## Estructura que funciona (5 a 8 slides)
1. **Portada** (`portada`): gancho + emoji + subtítulo que genera curiosidad ("El #3 lo comete casi todo el mundo").
2. **Desarrollo** (`punto`, `lista`, `pasos`, `comparacion`, `dato`, `cita`): un solo mensaje por slide, letra grande.
3. **Cierre** (`cta`): pregunta que conecta con la oferta + botón + "link en el perfil" + palabra para comentar + "like, guárdalo, compártelo".

Carruseles de valor (guías, errores, pasos, checklists) se guardan y comparten más: úsalos para educar y llevar a la oferta en el último slide.

## Plan JSON
```json
{
  "marca": "kallpa",
  "carruseles": [{
    "archivo": "2026-11-17-errores-app", "fecha": "2026-11-17", "hora": "13:00", "tema": "…", "palabra": "APP",
    "slides": [ { "tipo": "portada", "etiqueta": "🚫 Evítalos", "titulo": "…", "emoji": "💸", "sub": "…" } ],
    "caption": "…", "hashtags": ["#…"]
  }]
}
```

## Tipos de slide
| tipo | campos |
|---|---|
| portada | etiqueta, titulo, emoji, sub |
| punto | numero, titulo, emoji, texto |
| lista | titulo, items [[emoji, texto] ×3-6] |
| pasos | titulo, items [[título, detalle] ×3-5] |
| comparacion | titulo, antes[], despues[], etiqueta_antes, etiqueta_despues |
| dato | titulo, numero (texto, ej. "7 días"), etiqueta, texto |
| cita | texto, autor (solo citas reales o "cliente típico", nunca inventadas como reales) |
| cta | titulo, boton, sub, palabra |

## Reglas de diseño
- Máximo unas 25 palabras por slide (salvo listas cortas).
- Títulos de 2 a 4 líneas; si se ve apretado, acorta el texto antes que achicar la letra.
- Logo propio: pon `"logo": "ruta/logo.png"` en el perfil (PNG cuadrado con fondo transparente).
- Instagram permite hasta 20 imágenes por carrusel; Metricool recibe la lista de URLs en orden.
