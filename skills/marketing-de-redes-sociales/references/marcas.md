# Perfiles de marca (cualquier negocio)

Cada negocio tiene un archivo `assets/marcas/<id>.json`. Los scripts lo leen con `--marca <id>` (o una ruta).

## Campos
| campo | qué es |
|---|---|
| nombre, inicial, logo | Cómo se ve la marca. `logo` es opcional (PNG cuadrado); si no hay, se dibuja un cuadrado con la inicial. |
| usuario | @ de la red, se muestra en los carruseles |
| color1, color2 | Degradado principal (botones, logo, barra) |
| fondo, tema | Color de fondo y `oscuro` / `claro` |
| acento | Color para resaltar palabras y el botón "Desliza" |
| correo | Se muestra en la escena `agenda` |
| rubro, publico, oferta | Qué vende, a quién, y la oferta irresistible |
| cta_principal, primer_comentario | La acción que piden todas las piezas |
| tono, prohibido | Cómo habla la marca y qué nunca decir (precios, otras marcas, promesas falsas…) |
| metricool | blogId, red (instagram / tiktok / facebook) y zona horaria |
| hosting | Dónde se suben los archivos (ver metricool.md) |
| calendario | Días y horas de videos y carruseles |

## Para un negocio nuevo
1. Copia `_plantilla.json` a `assets/marcas/<id>.json`.
2. Si la persona da su web o redes, sácalas de ahí: colores (del logo o la web), tono, servicios, público y la oferta. Pregunta solo lo que falte y sea clave: la oferta, la acción que quiere (link, WhatsApp, comentar) y lo que no se debe decir.
3. Busca su marca en Metricool con `getBrandSettings` y guarda el blogId.
4. Haz una pieza de prueba (un video y un carrusel) y muéstrasela antes de programar en serie.

## Marcas actuales
- **kallpa**: apps web y software a medida para empresas. Oferta: reunión y demo gratis; si le gusta, la compra. CTA: link del perfil. Sin precios, sin cursos.
- **iamaster**: enseñanza de IA práctica para emprendedores peruanos. Sin precios en carruseles ni descripciones.
