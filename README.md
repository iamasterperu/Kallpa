# KALLPA

Web de KALLPA: apps web y software a medida para empresas, listos en 7 días o menos.

- `index.html`: la página (HTML/CSS/JS estático, sin compilación).
- `video/kallpa-presentacion.mp4`: video de presentación del inicio.
- `ESTRATEGIA.md`: estrategia comercial, guiones de anuncios y plan de 20 publicaciones.
- El calendario de citas y el pago se cargan desde la web de IA Master (`js/agenda.js` y `js/pago.js`) y usan el Apps Script `apps-script/IAMaster.gs` del repositorio `iamaster`.

## Publicar en Cloudflare
El Worker `kallpa` (kallpa.iamasterperu.workers.dev) se publica con `wrangler.jsonc`.
Para que se publique solo con cada cambio: Cloudflare → Workers & Pages → kallpa → Settings → Builds → Connect → este repositorio (rama `main`).
