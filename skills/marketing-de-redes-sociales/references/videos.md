# Videos 9:16 (Reels, TikTok, Shorts)

`scripts/video.py` convierte un plan JSON en videos de 1080×1920 con: animaciones por escena, voz de IA (Piper, `es_AR-daniela-high`, un poco más rápida y aguda para sonar animada), subtítulos grandes con palabras resaltadas, música sintetizada sin derechos de autor que baja cuando habla la voz, barra de progreso, logo de la marca y portada JPG.

## Estructura recomendada (18 a 30 s, 4 a 6 escenas)
1. `gancho` (2 a 4 s): el título más fuerte del video.
2. `problema`, `chat` o `antesdespues`: el dolor, mostrado.
3. `telefono`, `lista` o `chips`: la solución en acción.
4. `numero`, `lista` o `chips`: beneficio o prueba (plazo, horas ahorradas).
5. `cta`: la acción.

Videos de presentación (para la web) pueden durar 35 a 45 s y usar `agenda` para mostrar cómo se reserva.

## Plan JSON
```json
{
  "marca": "kallpa",
  "videos": [{
    "archivo": "2026-11-20-ventas", "dia": "viernes", "fecha": "2026-11-20", "hora": "19:00",
    "tema": "Panel de ventas en tiempo real", "palabra": "VENTAS", "resaltar": ["ventas", "celular"],
    "escenas": [ { "tipo": "gancho", "...": "...", "voz": "lo que dice la voz" } ],
    "caption": "…", "hashtags": ["#…"], "primer_comentario": "(opcional, si no usa el del perfil)"
  }]
}
```
Cada escena lleva `voz` (texto hablado; números en letras). La duración de cada escena sale sola de la voz.

## Tipos de escena
| tipo | campos | para qué |
|---|---|---|
| gancho | etiqueta, titulo, emoji, sub | Abrir fuerte |
| problema | titulo, items[3], contador (número, opcional), etiqueta | Lo que cuesta el problema (contador animado "-S/ 0 → -S/ 4,800") |
| chat | titulo, contacto, mensajes [["c" cliente / "k" negocio, texto] ×3] | Conversación de WhatsApp |
| telefono | titulo, app, kpis [[etiqueta, valor] ×2], filas[3], sello | La app o sistema funcionando |
| lista | titulo, items [[emoji, título, detalle] ×3-4] | Pasos, beneficios, errores |
| antesdespues | titulo, antes[3], despues[3] | Contraste |
| numero | titulo, numero, prefijo, sufijo, etiqueta | Un dato grande con contador |
| chips | titulo, emoji, chips[4-6] | Servicios, rubros, opciones |
| agenda | titulo, mes, mensaje | Calendario + hora + correo de confirmación |
| cta | detalle, bio (texto bajo el botón) | Cierre con la acción |

En `titulo`, `sub` y `etiqueta` se puede usar `<br>` y `<span class="y|g|r|v">` (acento, degradado de marca, rojo, verde).

## Consejos de calidad
- Textos en pantalla cortos: el título va en 2 o 3 líneas; los ítems, en 3 a 5 palabras.
- La voz no debe leer la pantalla palabra por palabra: complementa.
- La escena `cta` no muestra "comenta" si `palabra` está vacía (útil para la web).
- Para otra voz de Piper, cambia `VOZ` y `VOZ_URL` en `video.py` (voces en huggingface.co/rhasspy/piper-voices).
- El render toma unos 30 a 60 s por video; se hacen 3 en paralelo.
