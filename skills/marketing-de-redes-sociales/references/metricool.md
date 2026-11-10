# Programar en Metricool

## Antes de programar
1. `getBrandSettings`: obtén el `blogId` de la marca y comprueba que la red esté conectada (por ejemplo `networksData.instagramData = "kallpa_iamaster"`). Si la red no aparece, no programes. Dile a la persona que la conecte en Metricool (**Ajustes de la marca → Conectar red**; Instagram tiene que ser cuenta profesional vinculada a una página de Facebook). Conectar o desconectar redes solo lo puede hacer ella, porque Metricool pide su inicio de sesión.
2. `getScheduledPosts` del rango de fechas: no dupliques y cuenta cuántas quedan en el plan (el plan gratuito tiene un límite mensual).

## Archivos con URL pública
Metricool necesita una URL pública por archivo; al programar, la descarga y la guarda en su propio servidor (`static.metricool.com`). Opciones (`hosting.tipo` del perfil):
- **cloudflare_kv** (KALLPA): `publicar.py` sube cada archivo al KV `kallpa3d` con la API de Cloudflare (la clave la inyecta el entorno; nunca se escribe en archivos ni en el chat). El Worker de KALLPA los sirve en `https://kallpa.iamasterperu.workers.dev/v/<archivo>` (solo `.mp4` y `.jpg`, con nombres en minúsculas, números y guiones), y se borran solos a los 60 días.
- **url_publica**: archivos ya subidos a una carpeta web; `base_url` + nombre.
- **drive**: Google Drive enlazado en Metricool; la persona sube los archivos y se usan sus links.
- **ninguno**: entrega los archivos y `publicar.txt` para publicar a mano.

## Programar
`publicar.py` deja `metricool.json`: una lista de objetos `{date, blogId, info}`. Llama a `createScheduledPost` con cada uno tal cual.
- Reel: `providers [{network: instagram}]`, `instagramData {type: REEL, showReelOnFeed: true, isAiGenerated: true}`, `media [mp4]`, `videoThumbnailUrl` (portada).
- Carrusel: `instagramData {type: POST}`, `media` con todas las imágenes en orden.
- TikTok: `tiktokData {privacyOption: PUBLIC_TO_EVERYONE, isAigc: true}` en videos; en carruseles, `autoAddMusic: true`.
- Siempre `autoPublish: true`, `publicationDate {dateTime, timezone}` en la zona del perfil, `firstCommentText` con la CTA.
- La fecha no puede estar en el pasado.

## Mover o corregir
`updateScheduledPost` necesita `id`, `uuid` y el contenido **completo** (lo que no envíes se pierde). Usa como `media` las URLs `static.metricool.com/...` que devuelve Metricool. El `id` cambia tras cada edición; el `uuid` no. Metricool no tiene herramienta para borrar: si sobra una publicación, pídele a la persona que la elimine en el Planificador o reúsala moviéndola a otra fecha.

## Verificar
`getScheduledPosts` → todas en `PENDING`. Cuando se publica, el estado pasa a `PUBLISHED` con `publicUrl` (link del Reel).

## Dónde lo ve la persona
Metricool → Planificador → Calendario. También puedes publicar una galería (por ejemplo `/reels/` en la web de KALLPA) con todos los videos y sus fechas.
