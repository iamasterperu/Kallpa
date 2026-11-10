#!/usr/bin/env python3
"""Sube los archivos generados a un hosting público y arma las publicaciones listas para Metricool.

Uso:
  python3 publicar.py <plan.json> <carpeta_salida> --marca <perfil> [--solo-payloads]

- Sube cada video (.mp4 + portada .jpg) y cada carrusel (todas sus .jpg) según marca.hosting.
- Escribe en <carpeta_salida>/metricool.json la lista de publicaciones, una por elemento del plan:
    {"date": "...-05:00", "blogId": "...", "info": {...}}
  Claude usa cada objeto tal cual con la herramienta createScheduledPost de Metricool.
- Escribe <carpeta_salida>/publicar.txt con los textos y links, por si se publica a mano.

Hosting soportado (marca.hosting.tipo):
  cloudflare_kv  → sube a un KV de Cloudflare con la API (la clave la inyecta el entorno; nunca va en este archivo)
                   y se sirve desde un Worker con ruta /v/<archivo> (ver references/metricool.md).
  url_publica    → los archivos ya están en una carpeta pública: marca.hosting.base_url + nombre del archivo.
  ninguno / drive → no sube nada; deja los archivos listos para que la persona los suba (Drive enlazado a Metricool).
"""
import json, os, subprocess, sys
from datetime import datetime
from zoneinfo import ZoneInfo

AQUI = os.path.dirname(os.path.abspath(__file__))


def cargar_marca(m):
    if isinstance(m, str):
        p = m if os.path.exists(m) else os.path.join(AQUI, '..', 'assets', 'marcas', m + '.json')
        return json.load(open(p, encoding='utf-8'))
    return m or {}


def subir_kv(h, archivo, ruta):
    url = (f"https://api.cloudflare.com/client/v4/accounts/{h['cuenta']}/storage/kv/namespaces/{h['kv']}/values/"
           f"{h.get('prefijo', '')}{archivo}?expiration_ttl={h.get('dias', 60) * 86400}")
    r = subprocess.run(['curl', '-s', '-X', 'PUT', url, '-H', 'Content-Type: application/octet-stream', '--data-binary', '@' + ruta],
                       capture_output=True, text=True)
    if not json.loads(r.stdout or '{}').get('success'):
        sys.exit(f'❌ No se pudo subir {archivo}: {r.stdout[:300]}')
    print('✅ subido', archivo)


def fecha_iso(fecha, hora, zona):
    dt = datetime.fromisoformat(f'{fecha}T{hora}:00').replace(tzinfo=ZoneInfo(zona))
    if dt <= datetime.now(ZoneInfo(zona)):
        print(f'⚠ {fecha} {hora} ya pasó: Metricool rechazará esta publicación; cambia la fecha.')
    return dt.isoformat()


def main():
    plan, out = sys.argv[1], sys.argv[2]
    data = json.load(open(plan, encoding='utf-8'))
    marca = cargar_marca(sys.argv[sys.argv.index('--marca') + 1] if '--marca' in sys.argv else data.get('marca'))
    h = marca.get('hosting', {}) or {}; mc = marca.get('metricool', {}) or {}
    zona = mc.get('zona', 'America/Lima'); red = mc.get('red', 'instagram')
    solo_payloads = '--solo-payloads' in sys.argv
    base = h.get('base_url', '')
    items = [('video', v) for v in data.get('videos', [])] + [('carrusel', c) for c in data.get('carruseles', [])]
    posts, txt = [], []
    for tipo, it in items:
        a = it['archivo']
        if tipo == 'video':
            archivos = [a + '.mp4', a + '.jpg']
        else:
            archivos = sorted(f for f in os.listdir(out) if f.startswith(a + '-') and f[len(a) + 1:-4].isdigit() and f.endswith('.jpg'))
        if h.get('tipo') == 'cloudflare_kv' and not solo_payloads:
            for f in archivos:
                subir_kv(h, f, os.path.join(out, f))
        urls = [base + f for f in archivos] if base else []
        caption = (it.get('caption', '').strip() + '\n\n' + ' '.join(it.get('hashtags', []))).strip()
        txt.append(f"=== {it.get('dia', '')} {it['fecha']} {it['hora']} · {tipo.upper()} · {it.get('tema', '')} ===\n" +
                   '\n'.join(urls or archivos) + f"\n\n{caption}\n")
        if not urls:
            continue
        info = {'autoPublish': True, 'draft': False, 'descendants': [], 'hasNotReadNotes': False, 'shortener': False,
                'smartLinkData': {'ids': []}, 'mediaAltText': [], 'providers': [{'network': red}], 'text': caption,
                'firstCommentText': it.get('primer_comentario') or marca.get('primer_comentario', ''),
                'publicationDate': {'dateTime': f"{it['fecha']}T{it['hora']}:00", 'timezone': zona}}
        if tipo == 'video':
            info['media'] = [urls[0]]; info['videoThumbnailUrl'] = urls[1]
            if red == 'instagram':
                info['instagramData'] = {'type': 'REEL', 'showReelOnFeed': True, 'isAiGenerated': True}
            elif red == 'tiktok':
                info['tiktokData'] = {'privacyOption': 'PUBLIC_TO_EVERYONE', 'isAigc': True, 'title': it.get('tema', '')[:90]}
            elif red == 'facebook':
                info['facebookData'] = {'type': 'REEL'}
        else:
            info['media'] = urls
            if red == 'instagram':
                info['instagramData'] = {'type': 'POST', 'isAiGenerated': False}
            elif red == 'tiktok':
                info['tiktokData'] = {'privacyOption': 'PUBLIC_TO_EVERYONE', 'title': it.get('tema', '')[:90], 'autoAddMusic': True}
            elif red == 'facebook':
                info['facebookData'] = {'type': 'POST'}
        posts.append({'date': fecha_iso(it['fecha'], it['hora'], zona), 'blogId': str(mc.get('blogId', '')), 'info': info})
    json.dump(posts, open(os.path.join(out, 'metricool.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    open(os.path.join(out, 'publicar.txt'), 'w', encoding='utf-8').write('\n'.join(txt))
    print(f'Listo: {len(posts)} publicaciones en {os.path.join(out, "metricool.json")} · textos en publicar.txt')
    if not mc.get('blogId'):
        print('⚠ Falta marca.metricool.blogId: búscalo con getBrandSettings antes de programar.')


if __name__ == '__main__':
    main()
