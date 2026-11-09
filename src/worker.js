// KALLPA 3D · servidor: proyectos de inmobiliarias, IA para leer planos, videos y publicación.
import Anthropic from '@anthropic-ai/sdk';
import { zodOutputFormat } from '@anthropic-ai/sdk/helpers/zod';
import { z } from 'zod';

const MAX_VIDEO = 24 * 1024 * 1024;   // límite de un valor en KV (25 MiB)
const MAX_IMAGE = 6 * 1024 * 1024;
const AI_PER_DAY = 40;                 // lecturas de planos con IA por proyecto y por día

const json = (data, status = 200, extra = {}) => new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...extra } });
const err = (msg, status = 400) => json({ error: msg }, status);
const rid = (n = 10) => { const a = new Uint8Array(n); crypto.getRandomValues(a); return [...a].map(b => 'abcdefghijkmnpqrstuvwxyz23456789'[b % 32]).join(''); };
async function sha(s) { const h = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)); return [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, '0')).join(''); }
function safeEq(a, b) { if (a.length !== b.length) return false; let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; }
const clean = (s, n = 80) => String(s ?? '').replace(/[\u0000-\u001f]/g, '').trim().slice(0, n);

async function getProject(env, pid) { return pid && /^[a-z0-9]{4,20}$/.test(pid) ? env.K3D.get('p:' + pid, 'json') : null; }
// Cada empresa tiene su propia app con un único proyecto ("main"), sin contraseñas.
async function authed(req, env, pid) {
  if (pid !== 'main') return null;
  let p = await getProject(env, 'main');
  if (!p) { p = { id: 'main', name: 'Mi proyecto', inmo: { name: '', phone: '', web: '' }, depas: [], created: Date.now(), publishedAt: null }; await env.K3D.put('p:main', JSON.stringify(p)); }
  return p;
}
const publicProject = p => ({ id: p.id, name: p.name, inmo: p.inmo || {}, depas: p.depas || [], publishedAt: p.publishedAt || null });

/* ---------- IA: plano (2D o 3D) → ambientes ---------- */
const TIPOS = ['sala', 'comedor', 'cocina', 'dormitorio', 'dormitorio2', 'bano', 'lavanderia', 'estudio', 'pasillo', 'escalera', 'terraza'];
const PlanSchema = z.object({
  imagen_ancho_m: z.number().describe('Cuántos metros reales abarca el ancho COMPLETO de la imagen, de borde a borde.'),
  ambientes: z.array(z.object({
    tipo: z.enum(TIPOS),
    nombre: z.string(),
    x: z.number(), y: z.number(), ancho: z.number(), largo: z.number(),
  })),
  notas: z.string().describe('Breve, en español: supuestos hechos (por ejemplo medidas estimadas).'),
});
const SYSTEM = `Eres un arquitecto que convierte planos de departamentos en una lista de ambientes rectangulares vistos desde arriba.
La imagen puede ser un plano 2D o una vista 3D en perspectiva o isométrica: en ambos casos deduce la distribución en planta.
Reglas:
- Coordenadas en metros. Origen (0,0) = esquina superior izquierda de la IMAGEN completa; x crece a la derecha, y crece hacia abajo. x,y son la esquina superior izquierda de cada ambiente; ancho es en x, largo es en y.
- Usa las cotas escritas en el plano cuando existan. Si no hay cotas, estima la escala con muebles estándar (cama de 2 plazas 1.60 m de ancho, cama de 1 plaza 0.95 m, inodoro 0.70 m de largo, puerta 0.85 m).
- Los ambientes no se superponen. Ambientes vecinos comparten exactamente el mismo borde (misma coordenada). Redondea a 0.05 m.
- Simplifica formas en L o diagonales en rectángulos; si un ambiente es en L, divídelo en dos rectángulos del mismo tipo.
- Tipos: sala, comedor, cocina, dormitorio (principal, el más grande), dormitorio2 (otros dormitorios y cuarto de servicio), bano, lavanderia (también patio de servicio), estudio, pasillo (pasillos, hall, recibo, circulación), escalera, terraza (también balcón).
- Incluye los pasillos y halls como ambientes 'pasillo' para que todo quede conectado. Si sala y comedor están en un mismo espacio, sepáralos en dos rectángulos vecinos.
- nombre en español, corto (ej. "Dormitorio 2", "Baño de visitas").`;

async function analyzePlan(env, b64, mediaType, hint) {
  const client = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY });
  const res = await client.beta.messages.parse({
    model: 'claude-opus-5-5',
    max_tokens: 16000,
    thinking: { type: 'adaptive' },
    output_config: { effort: 'high', format: zodOutputFormat(PlanSchema) },
    betas: ['server-side-fallback-2026-07-01'],
    fallbacks: 'default',
    system: SYSTEM,
    messages: [{ role: 'user', content: [
      { type: 'image', source: { type: 'base64', media_type: mediaType, data: b64 } },
      { type: 'text', text: 'Convierte este plano en la lista de ambientes.' + (hint ? ` Dato del usuario: ${hint}` : '') },
    ] }],
  });
  if (res.stop_reason === 'refusal') throw new Error('La IA no pudo procesar esta imagen.');
  if (res.stop_reason === 'max_tokens' || !res.parsed_output) throw new Error('La IA no devolvió un resultado completo. Intenta con una imagen más clara.');
  return res.parsed_output;
}

/* ---------- media en KV con soporte de rango (necesario para video en iPhone) ---------- */
async function serveMedia(req, env, key, fallbackType) {
  const { value, metadata } = await env.K3D.getWithMetadata(key, 'arrayBuffer');
  if (!value) return new Response('No encontrado', { status: 404 });
  const type = (metadata && metadata.type) || fallbackType || 'application/octet-stream', size = value.byteLength;
  const base = { 'content-type': type, 'accept-ranges': 'bytes', 'cache-control': 'public, max-age=31536000, immutable' };
  const range = req.headers.get('range'), m = range && /bytes=(\d*)-(\d*)/.exec(range);
  if (m) {
    let start = m[1] === '' ? Math.max(0, size - parseInt(m[2], 10)) : parseInt(m[1], 10);
    let end = m[1] !== '' && m[2] !== '' ? Math.min(size - 1, parseInt(m[2], 10)) : size - 1;
    if (start >= size || start > end) return new Response(null, { status: 416, headers: { 'content-range': `bytes */${size}` } });
    return new Response(value.slice(start, end + 1), { status: 206, headers: { ...base, 'content-range': `bytes ${start}-${end}/${size}`, 'content-length': String(end - start + 1) } });
  }
  return new Response(value, { headers: { ...base, 'content-length': String(size) } });
}

async function api(req, env, parts) {
  const method = req.method;
  // Página pública
  if (parts[0] === 'pub' && parts[1] && method === 'GET') {
    const pub = await env.K3D.get('pub:' + parts[1], 'json');
    if (!pub) return err('Este proyecto aún no está publicado.', 404);
    return json(pub, 200, { 'cache-control': 'public, max-age=30' });
  }
  if (parts[0] !== 'projects' || !parts[1]) return err('Ruta no encontrada', 404);
  const pid = parts[1], p = await authed(req, env, pid);
  if (!p) return err('Proyecto no encontrado.', 404);
  const save = () => env.K3D.put('p:' + pid, JSON.stringify(p));

  if (parts.length === 2) {
    if (method === 'GET') return json({ ...publicProject(p) });
    if (method === 'PUT') { const b = await req.json().catch(() => ({})); p.name = clean(b.name) || p.name; p.inmo = { name: clean(b.inmo?.name), phone: clean(b.inmo?.phone, 30), web: clean(b.inmo?.web, 120) }; await save(); return json(publicProject(p)); }
  }
  if (parts[2] === 'publish' && method === 'POST') {
    const depas = [];
    for (const d of p.depas) {
      const dr = await env.K3D.get(`d:${pid}:${d.id}`, 'json');
      if (dr && dr.data && dr.data.floors && dr.data.floors.some(f => f.rooms && f.rooms.length)) depas.push({ id: d.id, name: d.name, info: dr.info || {}, data: dr.data, plan: dr.plan || null, video: dr.video || null });
    }
    if (!depas.length) return err('Agrega al menos un departamento con ambientes antes de publicar.');
    p.publishedAt = Date.now();
    await env.K3D.put('pub:' + pid, JSON.stringify({ ...publicProject(p), depas }));
    await save();
    return json({ ok: true, publishedAt: p.publishedAt, count: depas.length });
  }
  if (parts[2] !== 'depas') return err('Ruta no encontrada', 404);
  if (parts.length === 3 && method === 'POST') {
    if (p.depas.length >= 40) return err('Máximo 40 departamentos por proyecto.');
    const b = await req.json().catch(() => ({}));
    const d = { id: rid(6), name: clean(b.name, 60) || 'Depa ' + (p.depas.length + 1) };
    p.depas.push(d); await save();
    await env.K3D.put(`d:${pid}:${d.id}`, JSON.stringify({ name: d.name, data: null, info: {}, plan: null, video: null }));
    return json(d, 201);
  }
  const did = parts[3], di = p.depas.findIndex(d => d.id === did);
  if (di < 0) return err('Departamento no encontrado', 404);
  const dkey = `d:${pid}:${did}`;
  const draft = async () => (await env.K3D.get(dkey, 'json')) || { data: null, info: {}, plan: null, video: null };

  if (parts.length === 4) {
    if (method === 'GET') return json({ id: did, name: p.depas[di].name, ...(await draft()) });
    if (method === 'PUT') {
      const b = await req.json().catch(() => null); if (!b) return err('Datos no válidos');
      const s = JSON.stringify(b.data || null); if (s.length > 400000) return err('El plano es demasiado grande.');
      const dr = await draft();
      dr.data = b.data || null; dr.info = { m2: +b.info?.m2 || 0, dorms: +b.info?.dorms || 0, banos: +b.info?.banos || 0, precio: clean(b.info?.precio, 40) };
      if (b.name) { p.depas[di].name = clean(b.name, 60); dr.name = p.depas[di].name; await save(); }
      await env.K3D.put(dkey, JSON.stringify(dr));
      return json({ ok: true });
    }
    if (method === 'DELETE') {
      p.depas.splice(di, 1); await save(); await env.K3D.delete(dkey);
      return json({ ok: true });
    }
  }
  if (parts[4] === 'plan' || parts[4] === 'video') {
    if (method !== 'PUT') return err('Método no permitido', 405);
    const kind = parts[4], type = (req.headers.get('content-type') || '').split(';')[0].trim();
    const okType = kind === 'plan' ? /^image\/(jpeg|png|webp)$/.test(type) : /^video\/(mp4|webm)$/.test(type);
    if (!okType) return err('Tipo de archivo no permitido');
    const buf = await req.arrayBuffer();
    if (buf.byteLength > (kind === 'plan' ? MAX_IMAGE : MAX_VIDEO)) return err(kind === 'video' ? 'El video pesa más de 24 MB. Genera uno más corto o en menor calidad.' : 'La imagen es muy pesada.');
    const stamp = rid(8), key = `m:${pid}:${did}:${kind}:${stamp}`;
    await env.K3D.put(key, buf, { metadata: { type } });
    const dr = await draft();
    const pub = await env.K3D.get('pub:' + pid, 'json');
    const live = pub && pub.depas.some(x => x.id === did && x[kind] === dr[kind]);
    if (dr[kind] && !live) await env.K3D.delete(`m:${pid}:${did}:${kind}:${dr[kind]}`);
    dr[kind] = stamp; await env.K3D.put(dkey, JSON.stringify(dr));
    return json({ ok: true, stamp, url: `/media/${pid}/${did}/${kind}/${stamp}` });
  }
  if (parts[4] === 'analyze' && method === 'POST') {
    if (!env.ANTHROPIC_API_KEY) return err('La lectura automática de planos aún no está activada (falta la clave de IA en Cloudflare).', 503);
    const day = new Date().toISOString().slice(0, 10), ck = `ai:${pid}:${day}`;
    const used = parseInt((await env.K3D.get(ck)) || '0', 10);
    if (used >= AI_PER_DAY) return err('Llegaste al límite de lecturas con IA de hoy. Intenta mañana.', 429);
    const b = await req.json().catch(() => null);
    if (!b || typeof b.image !== 'string' || !/^image\/(jpeg|png|webp)$/.test(b.media_type || '')) return err('Imagen no válida');
    if (b.image.length > 7_000_000) return err('La imagen es muy pesada.');
    await env.K3D.put(ck, String(used + 1), { expirationTtl: 172800 });
    try { return json(await analyzePlan(env, b.image, b.media_type, clean(b.hint, 200))); }
    catch (e) {
      if (e instanceof Anthropic.RateLimitError) return err('La IA está ocupada, intenta en un minuto.', 503);
      if (e instanceof Anthropic.AuthenticationError) return err('La clave de IA configurada no es válida.', 503);
      if (e instanceof Anthropic.APIError) return err('La IA no respondió bien (' + e.status + '). Intenta de nuevo.', 502);
      return err(e.message || 'No se pudo leer el plano.', 502);
    }
  }
  return err('Ruta no encontrada', 404);
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url), parts = url.pathname.split('/').filter(Boolean);
    try {
      if (parts[0] === 'api') return await api(req, env, parts.slice(1));
      if (parts[0] === 'media' && parts.length === 5 && req.method === 'GET') {
        const [, pid, did, kind, stamp] = parts;
        if (!['plan', 'video'].includes(kind) || ![pid, did, stamp].every(s => /^[a-z0-9]{4,24}$/.test(s))) return new Response('No encontrado', { status: 404 });
        return await serveMedia(req, env, `m:${pid}:${did}:${kind}:${stamp}`);
      }
      // Videos y portadas para redes sociales (los sube la fábrica de videos semanal)
      if (parts[0] === 'v' && parts.length === 2 && (req.method === 'GET' || req.method === 'HEAD')) {
        const m = /^[a-z0-9-]{3,80}\.(mp4|jpg)$/.exec(parts[1]);
        if (!m) return new Response('No encontrado', { status: 404 });
        return await serveMedia(req, env, 'soc:' + parts[1], m[1] === 'mp4' ? 'video/mp4' : 'image/jpeg');
      }
      if (parts[0] === 'p' || parts[0] === 'panel') {
        if (parts[0] === 'panel' && url.pathname === '/panel') return Response.redirect(url.origin + '/panel/' + url.search, 301);
        const r = await env.ASSETS.fetch(new Request(new URL('/recorrido/', url.origin), req));
        const h = new Headers(r.headers); h.set('cache-control', 'no-cache');
        if (parts[0] === 'panel') h.set('x-robots-tag', 'noindex');
        return new Response(r.body, { status: r.status, headers: h });
      }
      return env.ASSETS.fetch(req);
    } catch (e) {
      return err('Error del servidor', 500);
    }
  },
};
