#!/usr/bin/env python3
"""Generador de carruseles 4:5 (1080x1350) para Instagram, Facebook, LinkedIn y TikTok (modo foto).

Uso:  python3 carrusel.py <plan.json> <carpeta_salida> [--solo N]

El JSON trae "marca" y una lista "carruseles"; cada carrusel tiene sus "slides".
Tipos de slide: portada, punto, lista, comparacion, dato, cita, pasos, cta.
Salida por carrusel: <archivo>-01.jpg, <archivo>-02.jpg… y <archivo>-vista.jpg (todas en fila para revisar).
Ejemplo completo: ../assets/ejemplos/carruseles-semana.json
"""
import html, json, os, re, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
MARCA = {'nombre': 'MI MARCA', 'inicial': 'M', 'usuario': '', 'color1': '#22d3ee', 'color2': '#8b5cf6',
         'fondo': '#070b18', 'acento': '#facc15', 'logo': '', 'tema': 'oscuro'}


def e(s):
    return html.escape(str(s))


def rico(s):  # permite <br> y <span class="y|g|r|v"> en los títulos
    s = html.escape(str(s))
    s = re.sub(r'&lt;span class=&quot;(y|g|r|v)&quot;&gt;', r'<span class="\1">', s)
    return s.replace('&lt;/span&gt;', '</span>').replace('&lt;br&gt;', '<br>')


def logo():
    if MARCA.get('logo'):
        src = MARCA['logo'] if re.match(r'^(https?:|data:|file:)', MARCA['logo']) else 'file://' + os.path.abspath(MARCA['logo'])
        return f'<img class="mk img" src="{e(src)}" alt="">'
    return f'<div class="mk">{e(MARCA.get("inicial") or MARCA["nombre"][:1])}</div>'


def slide_html(s, i, n):
    t = s['tipo']; d = lambda k: s.get(k, '')
    if t == 'portada':
        body = (f'<div class="tag">{e(d("etiqueta"))}</div>' if d('etiqueta') else '') + \
               f'<h1 class="h big">{rico(d("titulo"))}</h1>' + \
               (f'<div class="emo">{e(d("emoji"))}</div>' if d('emoji') else '') + \
               (f'<p class="sub">{rico(d("sub"))}</p>' if d('sub') else '')
    elif t == 'punto':
        body = f'<div class="num">{e(d("numero"))}</div><h2 class="h">{rico(d("titulo"))}</h2>' + \
               (f'<div class="emo m">{e(d("emoji"))}</div>' if d('emoji') else '') + f'<p class="txt">{rico(d("texto"))}</p>'
    elif t == 'lista':
        it = ''.join(f'<div class="li"><em>{e(x[0])}</em><span>{rico(x[1])}</span></div>' for x in s.get('items', [])[:6])
        body = f'<h2 class="h">{rico(d("titulo"))}</h2><div class="lista">{it}</div>'
    elif t == 'pasos':
        it = ''.join(f'<div class="paso"><b>{k + 1}</b><div><strong>{rico(x[0])}</strong><span>{rico(x[1] if len(x) > 1 else "")}</span></div></div>' for k, x in enumerate(s.get('items', [])[:5]))
        body = f'<h2 class="h">{rico(d("titulo"))}</h2><div class="pasos">{it}</div>'
    elif t == 'comparacion':
        a = ''.join(f'<div>❌ {rico(x)}</div>' for x in s.get('antes', [])[:5])
        b = ''.join(f'<div>✅ {rico(x)}</div>' for x in s.get('despues', [])[:5])
        body = f'<h2 class="h">{rico(d("titulo"))}</h2><div class="cmp"><div class="col no"><h3>{e(d("etiqueta_antes") or "Antes")}</h3>{a}</div><div class="col si"><h3>{e(d("etiqueta_despues") or "Después")}</h3>{b}</div></div>'
    elif t == 'dato':
        body = f'<h2 class="h">{rico(d("titulo"))}</h2><div class="dato g">{e(d("numero"))}</div><p class="lbl">{rico(d("etiqueta"))}</p>' + \
               (f'<p class="txt">{rico(d("texto"))}</p>' if d('texto') else '')
    elif t == 'cita':
        body = f'<div class="comillas">“</div><p class="cita">{rico(d("texto"))}</p>' + (f'<p class="autor">— {e(d("autor"))}</p>' if d('autor') else '')
    elif t == 'cta':
        body = f'<div class="logo">{logo()}<span>{e(MARCA["nombre"])}</span></div><h2 class="h">{rico(d("titulo"))}</h2>' + \
               f'<div class="boton">{rico(d("boton") or "📅 Agenda GRATIS")}</div><p class="sub">{rico(d("sub") or "👆 Link en nuestro perfil")}</p>' + \
               (f'<p class="com">💬 o comenta <b>"{e(d("palabra"))}"</b></p>' if d('palabra') else '') + \
               '<div class="acciones"><span>❤️ Dale like</span><span>🔖 Guárdalo</span><span>📤 Compártelo</span></div>'
    else:
        raise ValueError('Tipo de slide desconocido: ' + t)
    flecha = '<div class="desliza">Desliza →</div>' if i < n - 1 else ''
    puntos = ''.join(f'<i class="{"on" if k == i else ""}"></i>' for k in range(n))
    return f'''<section class="slide s-{t}" style="--pos:{i}"><div class="bg"></div><div class="linea"></div>
<header><div class="marca">{logo()}<span>{e(MARCA["nombre"])}</span></div><div class="user">{e(MARCA.get("usuario", ""))}</div></header>
<main>{body}</main><footer><div class="dots">{puntos}</div>{flecha}<div class="cont">{i + 1}/{n}</div></footer></section>'''


def hacer(c, out):
    slides = c['slides']; n = len(slides)
    page = os.path.join(AQUI, f'_{c["archivo"]}.html')
    m = MARCA
    css_vars = f':root{{--c1:{m["color1"]};--c2:{m["color2"]};--bg:{m["fondo"]};--acento:{m["acento"]};--n:{n}}}'
    claro = ' claro' if m.get('tema') == 'claro' else ''
    with open(page, 'w', encoding='utf-8') as f:
        f.write(f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="plantilla_carrusel.css"><style>{css_vars}</style></head>'
                f'<body class="{claro}">' + ''.join(slide_html(s, i, n) for i, s in enumerate(slides)) + '</body></html>')
    subprocess.run(['node', os.path.join(AQUI, 'render_carrusel.cjs'), page, os.path.join(out, c['archivo'])], check=True)
    os.remove(page)
    from PIL import Image
    ims = [Image.open(os.path.join(out, f'{c["archivo"]}-{k + 1:02d}.jpg')) for k in range(n)]
    w = 360; h = int(w * 1350 / 1080)
    vista = Image.new('RGB', (w * n + 10 * (n - 1), h), 'white')
    for k, im in enumerate(ims):
        vista.paste(im.resize((w, h)), (k * (w + 10), 0))
    vista.save(os.path.join(out, f'{c["archivo"]}-vista.jpg'), quality=85)
    print(f'✅ {c["archivo"]}: {n} slides', flush=True)


def main():
    spec, out = sys.argv[1], sys.argv[2]
    solo = int(sys.argv[sys.argv.index('--solo') + 1]) if '--solo' in sys.argv else None
    os.makedirs(out, exist_ok=True)
    data = json.load(open(spec, encoding='utf-8'))
    m = data.get('marca')
    if '--marca' in sys.argv:
        m = sys.argv[sys.argv.index('--marca') + 1]
    if isinstance(m, str):  # ruta a un perfil de marca (assets/marcas/*.json)
        m = json.load(open(m if os.path.exists(m) else os.path.join(AQUI, '..', 'assets', 'marcas', m + '.json'), encoding='utf-8'))
    MARCA.update(m or {})
    for i, c in enumerate(data['carruseles']):
        if solo is None or i == solo:
            hacer(c, out)


if __name__ == '__main__':
    main()
