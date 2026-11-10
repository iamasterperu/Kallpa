#!/usr/bin/env python3
"""Carruseles CONTINUOS 3:4 (estilo IAMASTER): un lienzo de N×1080 por 1440 cortado en N slides.

Uso: python3 carrusel_panorama.py <plan.json> <carpeta_salida> [--solo N] [--marca iamaster]

Cada carrusel del plan: {"archivo","tema","palabra","tema_visual": "crema|noche|vibrante","slides":[...],"cruza": {...}}
Tipos de slide:
  portada     tag, titulo, acento, texto, mascota, nota (lista de líneas: una nota que cruza al slide 2)
  prompt      over, titulo, acento, prompts [{titulo, texto}] (usa [corchetes] para lo que la persona cambia), tip, mascota
  lista       over, titulo, acento, items [[num/emoji, negrita, detalle]], mascota
  comparacion over, titulo, acento, antes {titulo, items}, despues {titulo, items}
  juego       over, titulo, acento, opciones [texto…] (numeradas, para votar o marcar), mascota
  cta         over, titulo, acento, oferta (true = cursos de la marca), palabra, pregunta, mascota
"cruza": {"img": "cuerda", "entre": 3, "alto": 560, "arriba": 560}  → la mascota queda sobre el corte entre el slide 3 y el 4.
Mascotas: assets/mascotas/<marca>/<nombre>.png. Salida: <archivo>-01.jpg … y <archivo>-vista.jpg.
"""
import html, json, os, re, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1440
MASC = os.path.join(AQUI, '..', 'assets', 'mascotas', 'iamaster')
CURSOS = ['Crea tu Web', 'Agente de voz + correo automático', 'Crea tu juego 2D']


def e(s):
    return html.escape(str(s))


def rico(s):  # [algo] → resaltado amarillo; *algo* → negrita
    s = e(s)
    s = re.sub(r'\[([^\]]+)\]', r'<u>[\1]</u>', s)
    return re.sub(r'\*([^*]+)\*', r'<b>\1</b>', s)


def masc(nombre, estilo):
    src = 'file://' + os.path.abspath(os.path.join(MASC, nombre + '.png'))
    return f'<img class="masc" src="{src}" style="{estilo}">'


def bloque_titulo(s, grande=False):
    out = ''
    if s.get('tag'): out += f'<span class="tag">{e(s["tag"])}</span>'
    if s.get('over'): out += f'<div class="over">{e(s["over"])}</div>'
    fs = s.get('tam', 108 if grande else 92)
    out += f'<div class="h" style="font-size:{fs}px;margin-top:{30 if grande else 16}px">{e(s["titulo"]).replace("|", "<br>")}</div>'
    if s.get('acento'):
        out += f'<div class="it" style="font-size:{int(fs * (1.15 if grande else 1.3))}px;margin-top:4px">{e(s["acento"])}</div>'
    if s.get('texto'):
        out += f'<div class="p" style="margin-top:26px;max-width:800px">{rico(s["texto"])}</div>'
    return out


def slide_html(s, i, n, palabra):
    t = s['tipo']; x = i * W
    body, extra = '', ''
    m = s.get('mascota')
    if t == 'portada':
        body = bloque_titulo(s, True)
        if m: extra += masc(m, f'left:{x + 80}px;top:{1270 - 390}px;height:390px')
        if s.get('nota'):
            lineas = ''.join(f'<div>{e(l)}</div>' for l in s['nota'])
            extra += f'<div class="abs nota" style="left:{x + 700}px;top:860px">{lineas}</div>'
        extra += f'<div class="abs desliza" style="left:{x + (520 if m else 70)}px;top:1190px;z-index:10">Desliza <b>→</b></div>'
    elif t == 'prompt':
        body = bloque_titulo(s)
        for k, p in enumerate(s['prompts']):
            body += (f'<div class="prompt" style="margin-top:{40 if k == 0 else 26}px;max-width:{s.get("ancho", 820)}px"><div class="ph"><span>PROMPT {k + 1:02d} · COPIAR</span><i>COPIAR</i></div>'
                     + (f'<h4>{e(p["titulo"])}</h4>' if p.get('titulo') else '') + f'<p>{rico(p["texto"])}</p></div>')
        if s.get('tip'): body += f'<div class="p" style="margin-top:26px;max-width:640px;font-size:27px">💡 {rico(s["tip"])}</div>'
        if m: extra += masc(m, f'right:{(n - 1 - i) * W + 120}px;top:{1270 - 300}px;height:300px')
    elif t == 'lista':
        body = bloque_titulo(s)
        it = ''.join(f'<div class="fila"><b>{e(a)}</b><div><strong>{e(bb)}</strong><span>{e(c)}</span></div></div>' for a, bb, c in s['items'])
        body += f'<div class="filas">{it}</div>'
        if m: extra += masc(m, f'right:{(n - 1 - i) * W + 120}px;top:{1270 - 300}px;height:300px')
    elif t == 'comparacion':
        body = bloque_titulo(s)
        a, d = s['antes'], s['despues']
        col = lambda c, cls, ic: f'<div class="col {cls}"><h5>{e(c["titulo"])}</h5>' + ''.join(f'<div class="ci"><i>{ic}</i>{rico(z)}</div>' for z in c['items']) + '</div>'
        body += f'<div class="cmp">{col(a, "no", "✕")}{col(d, "si", "✓")}</div>'
        if m: extra += masc(m, f'right:{(n - 1 - i) * W + 120}px;top:{1270 - 280}px;height:280px')
    elif t == 'juego':
        body = bloque_titulo(s)
        it = ''.join(f'<div class="op"><b>{s.get("inicio", 1) + k}</b>{rico(z)}</div>' for k, z in enumerate(s['opciones']))
        body += f'<div class="ops">{it}</div>'
        if m: extra += masc(m, f'right:{(n - 1 - i) * W + 120}px;top:{1270 - 300}px;height:300px')
    elif t == 'cta':
        body = bloque_titulo(s)
        if s.get('oferta', True):
            cur = ''.join(f'<div class="curso{" on" if k == 0 else ""}"><i>✓</i>{e(c)}</div>' for k, c in enumerate(CURSOS))
            body += f'<div class="oferta" style="margin-top:40px;width:620px"><div class="ot">CURSOS GRABADOS · A TU RITMO · ACCESO DE POR VIDA</div>{cur}</div>'
        body += f'<div style="margin-top:44px"><span class="pill">{e(s.get("boton") or f"Comenta “{palabra}” y te paso {s.get("regalo", "los prompts")}")}</span></div>'
        if s.get('pregunta'): body += f'<div class="pregunta" style="margin-top:26px;max-width:800px">{e(s["pregunta"])}</div>'
        if m: extra += masc(m, f'right:{(n - 1 - i) * W + 115}px;top:{s.get("masc_top", 600)}px;height:320px')
    else:
        raise ValueError('tipo de slide desconocido: ' + t)
    cab = (f'<div class="cab" style="left:{x + 70}px"><div class="marca"><div class="mk">IA</div>MASTER</div>'
           f'<div class="cont">{i + 1:02d} / {n:02d}</div></div>')
    pl = (';padding-left:200px' if s.get('_tras_cruce') else '') + (';padding-right:240px' if s.get('_antes_cruce') else '')
    return f'{cab}<div class="slide" style="left:{x}px{pl}">{body}</div>{extra}'


LUCES = {'crema': ['r', 'n', 'y', 'r', 'n', 'y'], 'noche': ['m', 'r', 'n', 'm', 'r', 'n'], 'vibrante': ['y', 'r', 'n', 'y', 'r', 'n']}


def pagina(c):
    n = len(c['slides']); tema = c.get('tema_visual', 'crema')
    luces = ''.join(f'<div class="luz {LUCES[tema][i % 6]}" style="left:{i * W + (600 if i % 2 else -150)}px;top:{-200 if i % 2 else 1050}px;width:650px;height:560px;opacity:{.45 if tema == "noche" else .35}"></div>' for i in range(n))
    wv = n * W
    path = f'M-20 1330 ' + ' '.join(f'S {k * 540 + 270} {1230 if k % 2 else 1400} {k * 540 + 540} 1320' for k in range(n * 2 + 1))
    linea = (f'<svg class="abs" style="left:0;top:0;z-index:1" width="{wv}" height="{H}"><defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#FF3D7F"/>'
             f'<stop offset=".5" stop-color="#FF8A00"/><stop offset="1" stop-color="#FF3D7F"/></linearGradient></defs>'
             f'<path d="{path}" fill="none" stroke="url(#g)" stroke-width="12" stroke-linecap="round" opacity=".9"/></svg>')
    if c.get('cruza') and c['cruza']['entre'] < n: c['slides'][c['cruza']['entre']]['_tras_cruce'] = True
    if c.get('cruza'): c['slides'][c['cruza']['entre'] - 1]['_antes_cruce'] = True
    slides = ''.join(slide_html(s, i, n, c['palabra']) for i, s in enumerate(c['slides']))
    cr = c.get('cruza')
    if cr:
        slides += masc(cr['img'], f'left:{cr["entre"] * W - 190}px;top:{cr.get("arriba", 560)}px;height:{cr.get("alto", 540)}px;z-index:9')
    css = 'file://' + os.path.join(AQUI, 'plantilla_panorama.css')
    return f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{css}"><style>#lienzo{{width:{wv}px}}</style></head>
<body><div id="lienzo" class="{tema}">{luces}{linea}{slides}</div></body></html>'''


def main():
    plan, out = sys.argv[1], sys.argv[2]
    solo = int(sys.argv[sys.argv.index('--solo') + 1]) if '--solo' in sys.argv else None
    os.makedirs(out, exist_ok=True)
    data = json.load(open(plan, encoding='utf-8'))
    for k, c in enumerate(data['carruseles']):
        if solo is not None and k != solo: continue
        p = os.path.join(out, f'_{c["archivo"]}.html')
        open(p, 'w', encoding='utf-8').write(pagina(c))
        subprocess.run(['node', os.path.join(AQUI, 'render_panorama.cjs'), p, str(len(c['slides'])), os.path.join(out, c['archivo'])], check=True)
        os.remove(p)
        print('✅', c['archivo'], len(c['slides']), 'slides', flush=True)


if __name__ == '__main__':
    main()
