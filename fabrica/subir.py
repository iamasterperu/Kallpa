#!/usr/bin/env python3
"""Sube los MP4 y JPG de una semana al KV de Cloudflare (se sirven en https://kallpa.iamasterperu.workers.dev/v/<archivo>)
y escribe publicar.txt con los textos. Uso: python3 fabrica/subir.py <semana.json> <carpeta_salida>
Los archivos se borran solos a los 60 días. La cuenta de Cloudflare la pone el entorno (no hay claves en este archivo)."""
import json, os, subprocess, sys
CUENTA = 'e00bb6696bb9104516496040a6d2a999'; KV = '7b626d98747c41aebe1afb513e7f81f4'
BASE = 'https://kallpa.iamasterperu.workers.dev/v/'
spec, out = sys.argv[1], sys.argv[2]
data = json.load(open(spec, encoding='utf-8'))
txt = []
for v in data['videos']:
    for ext in ('mp4', 'jpg'):
        f = os.path.join(out, f"{v['archivo']}.{ext}")
        url = f"https://api.cloudflare.com/client/v4/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/soc:{v['archivo']}.{ext}?expiration_ttl=5184000"
        r = subprocess.run(['curl', '-s', '-X', 'PUT', url, '-H', 'Content-Type: application/octet-stream', '--data-binary', '@' + f], capture_output=True, text=True)
        ok = json.loads(r.stdout or '{}').get('success')
        print(('✅' if ok else '❌'), v['archivo'] + '.' + ext, '' if ok else r.stdout[:300])
        if not ok: sys.exit(1)
    v['video_url'] = BASE + v['archivo'] + '.mp4'; v['portada_url'] = BASE + v['archivo'] + '.jpg'
    txt.append(f"=== {v['dia'].upper()} {v['fecha']} · {v['hora']} · {v['tema']} ===\nVideo: {v['video_url']}\n\n{v['caption']}\n\n{' '.join(v['hashtags'])}\n")
open(os.path.join(out, 'publicar.txt'), 'w', encoding='utf-8').write('\n'.join(txt))
json.dump(data, open(spec, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('Listo:', os.path.join(out, 'publicar.txt'))
