#!/usr/bin/env python3
"""Fábrica de Reels verticales 9:16 (1080x1920) para cualquier marca.

Uso:  python3 video.py <plan.json> <carpeta_salida> [--solo N]

El JSON trae un bloque "marca" (nombre, inicial, colores, correo); ver assets/ejemplos/videos-semana.json.

Cada video del JSON trae sus escenas (tipo + textos + lo que dice la voz).
La fábrica genera la voz (Piper, voz Daniela más animada), las animaciones,
la música, los subtítulos y une todo en un MP4 con su portada JPG.
Tipos de escena: gancho, problema, telefono, lista, antesdespues, numero, chips, chat, cta.
"""
import html, json, math, os, random, re, subprocess, sys, threading, urllib.request, wave
from concurrent.futures import ThreadPoolExecutor
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
LOCK = threading.Lock()
FPS = 30
VOZ_DIR = os.path.expanduser('~/.cache/piper-voces')
VOZ_URL = 'https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_AR/daniela/high/'
VOZ = 'es_AR-daniela-high.onnx'
RESALTAR = ['app', 'aplicación', 'aplicaciones', 'WhatsApp', 'Excel', 'gratis', 'siete', 'días', 'dinero', 'ventas', 'clientes',
            'automático', 'automática', 'inteligencia', 'artificial', 'perfil', 'comenta', 'Comenta', 'empresa', 'negocio', 'tiempo', 'horas']


def sh(*a):
    subprocess.run(a, check=True)


# ---------- voz ----------
def asegurar_voz():
    os.makedirs(VOZ_DIR, exist_ok=True)
    for f in (VOZ, VOZ + '.json'):
        p = os.path.join(VOZ_DIR, f)
        if not os.path.exists(p) or os.path.getsize(p) < 1000:
            print('Descargando voz', f)
            urllib.request.urlretrieve(VOZ_URL + f, p)
    from piper import PiperVoice
    return PiperVoice.load(os.path.join(VOZ_DIR, VOZ))


def decir(voz, texto, salida):
    """Voz Daniela un poco más rápida y aguda (más animada), normalizada a 44.1 kHz."""
    from piper import SynthesisConfig
    crudo = salida + '.raw.wav'
    with LOCK, wave.open(crudo, 'wb') as w:
        voz.synthesize_wav(texto, w, syn_config=SynthesisConfig(length_scale=0.84, noise_scale=0.8, noise_w_scale=0.85))
    with wave.open(crudo) as w:
        sr = w.getframerate()
    sh('ffmpeg', '-y', '-loglevel', 'error', '-i', crudo, '-af',
       f'asetrate={int(sr * 1.045)},aresample=44100,atempo={1 / 1.045:.5f},highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=60,loudnorm=I=-15:TP=-1.5:LRA=7',
       '-ac', '1', '-ar', '44100', salida)
    os.remove(crudo)
    with wave.open(salida) as w:
        return w.getnframes() / w.getframerate()


# ---------- música (sintetizada, sin derechos de autor) ----------
def musica(dur, semilla, salida):
    rnd = random.Random(semilla)
    sr = 44100
    bpm = rnd.choice([112, 116, 120, 124])
    beat = 60 / bpm
    raiz = rnd.choice([0, 2, 5, 7, 9])  # tonalidad
    progs = [[0, 7, 9, 5], [9, 5, 0, 7], [0, 5, 9, 7], [0, 9, 5, 7]]
    prog = rnd.choice(progs)
    n = int(dur * sr) + sr
    out = np.zeros(n)
    t = np.arange(n) / sr
    f = lambda semi: 220 * 2 ** ((semi + raiz - 9) / 12)

    def env(length, a=0.005, d=0.25):
        x = np.arange(length) / sr
        return np.minimum(1, x / a) * np.exp(-x / d)

    def add(start, sig):
        i = int(start * sr)
        if i >= n: return
        j = min(n, i + len(sig)); out[i:j] += sig[:j - i]

    total_beats = int(dur / beat) + 2
    for b in range(total_beats):
        st = b * beat
        L = int(0.35 * sr); x = np.arange(L) / sr
        add(st, 0.9 * np.sin(2 * np.pi * (50 + 90 * np.exp(-x * 30)) * x) * np.exp(-x * 9))  # bombo
        hl = int(0.06 * sr)
        add(st + beat / 2, 0.12 * np.random.default_rng(b).standard_normal(hl) * env(hl, 0.001, 0.02))  # hi-hat
        if b % 2 == 1:
            sl = int(0.18 * sr)
            add(st, 0.22 * np.random.default_rng(1000 + b).standard_normal(sl) * env(sl, 0.001, 0.05))  # palmas
        acorde = prog[(b // 4) % 4]
        for k in range(2):  # bajo en corcheas
            bl = int(beat / 2 * sr); xb = np.arange(bl) / sr
            add(st + k * beat / 2, 0.28 * np.sign(np.sin(2 * np.pi * f(acorde - 24) * xb)) * env(bl, 0.005, 0.12))
        notas = [acorde, acorde + 4 if acorde in (0, 5, 7) else acorde + 3, acorde + 7, acorde + 12]
        for k in range(4):  # arpegio
            al = int(beat / 4 * sr * 1.6); xa = np.arange(al) / sr
            fr = f(notas[(b * 4 + k) % 4] + 12)
            add(st + k * beat / 4, 0.1 * (np.sin(2 * np.pi * fr * xa) + 0.3 * np.sin(4 * np.pi * fr * xa)) * env(al, 0.003, 0.09))
        if b % 4 == 0:  # pad
            pl = int(4 * beat * sr); xp = np.arange(pl) / sr
            pad = sum(np.sin(2 * np.pi * f(s) * xp + 0.3 * np.sin(2 * np.pi * 0.5 * xp)) for s in notas[:3])
            add(st, 0.05 * pad * np.minimum(1, xp / 0.4) * np.minimum(1, (4 * beat - xp) / 0.4))
    out = out[:int(dur * sr)]
    fade = int(1.2 * sr); out[-fade:] *= np.linspace(1, 0, fade); out[:int(0.3 * sr)] *= np.linspace(0, 1, int(0.3 * sr))
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.8
    with wave.open(salida, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((out * 32767).astype(np.int16).tobytes())


# ---------- escenas ----------
MARCA = {'nombre': 'MI MARCA', 'inicial': 'M', 'color1': '#22d3ee', 'color2': '#8b5cf6', 'fondo': '#070b18', 'acento': '#facc15', 'correo': '', 'logo': ''}


def logo_html(grande):
    # Logo: imagen (ruta local o URL en marca.logo) o un cuadrado con la inicial y los colores de la marca
    if MARCA.get('logo'):
        src = MARCA['logo'] if re.match(r'^(https?:|data:|file:)', MARCA['logo']) else 'file://' + os.path.abspath(MARCA['logo'])
        return f'<img class="mk" style="object-fit:contain;background:none;transform:none" src="{html.escape(src)}" alt="">'
    return f'<div class="mk">{html.escape(MARCA.get("inicial") or MARCA["nombre"][:1])}</div>'


def e(s):  # texto plano escapado
    return html.escape(str(s))


def rico(s):  # permite <span class="y|g|r|v"> y <br> en títulos que escribimos nosotros
    s = html.escape(str(s))
    s = re.sub(r'&lt;span class=&quot;(y|g|r|v|it)&quot;&gt;', r'<span class="\1">', s)
    return s.replace('&lt;/span&gt;', '</span>').replace('&lt;br&gt;', '<br>')


def mascota_html(es):
    """Personaje de la marca (PNG sin fondo en marca.mascotas/<nombre>.png). "mascota": "salta" o {"img","lado","alto","arriba"}."""
    m = es.get('mascota')
    if not m or not MARCA.get('mascotas'):
        return ''
    if isinstance(m, str): m = {'img': m}
    carpeta = MARCA['mascotas'] if os.path.isabs(MARCA['mascotas']) else os.path.join(AQUI, '..', MARCA['mascotas'])
    src = 'file://' + os.path.abspath(os.path.join(carpeta, m['img'] + '.png'))
    lado = m.get('lado', 'der'); alto = int(m.get('alto', 430)); arriba = int(m.get('arriba', 1300 - alto))
    pos = {'der': 'right:30px', 'izq': 'left:30px', 'centro': f'left:calc(50% - {alto // 3}px)'}[lado]
    return (f'<img class="masc pop" style="{pos};top:{arriba}px;height:{alto}px;animation-delay:{m.get("delay", .5)}s" src="{html.escape(src)}" alt="">')


def escena_html(es, palabra):
    return escena_base(es, palabra) + mascota_html(es)


def escena_base(es, palabra):
    t = es['tipo']; d = lambda k: es.get(k, '')
    if t == 'gancho':
        tag = f'<div class="tag pop">{e(d("etiqueta"))}</div>' if d('etiqueta') else ''
        emo = '' if es.get('mascota') else f'<div class="emo pop float" style="animation-delay:.35s,1s">{e(d("emoji") or "🚀")}</div>'
        return f'{tag}<h1 class="h t1 pop">{rico(d("titulo"))}</h1>{emo}' + \
               (f'<div class="sub up" style="animation-delay:.9s">{rico(d("sub"))}</div>' if d('sub') else '')
    if t == 'problema':
        items = ''.join(f'<div class="ls left" style="animation-delay:{.4 + i * .55:.2f}s">{e(x)} <i>{e(es.get("marca_item", "-S/"))}</i></div>' for i, x in enumerate(es.get('items', [])[:4]))
        cont = f'<div class="money pop" style="animation-delay:{.4 + len(es.get("items", [])) * .55:.2f}s"><span class="count" data-to="{int(es.get("contador", 0))}" data-pre="-S/ " data-at="{.6 + len(es.get("items", [])) * .55:.2f}">-S/ 0</span><small>{e(d("etiqueta"))}</small></div>' if es.get('contador') else ''
        return f'<h2 class="h t2 up">{rico(d("titulo"))}</h2><div class="loss">{items}</div>{cont}'
    if t == 'telefono':
        kp = ''.join(f'<div class="kpi"><small>{e(a)}</small><b>{e(b)}</b></div>' for a, b in es.get('kpis', [])[:2])
        bars = ''.join(f'<div style="height:{h}%;animation-delay:{.9 + i * .15:.2f}s"></div>' for i, h in enumerate([40, 65, 50, 85, 100]))
        rows = ''.join(f'<div class="left" style="animation-delay:{1.7 + i * .25:.2f}s">{e(x)}</div>' for i, x in enumerate(es.get('filas', [])[:3]))
        sello = f'<div class="badge pop" style="animation-delay:2.3s">{e(d("sello"))}</div>' if d('sello') else ''
        return f'<h2 class="h t2 up">{rico(d("titulo"))}</h2><div class="phone pop" style="animation-delay:.4s"><div class="ph-h">{e(d("app"))}</div><div class="kpis">{kp}</div><div class="chart">{bars}</div><div class="rows">{rows}</div>{sello}</div>'
    if t == 'lista':
        it = ''.join(f'<div class="st left" style="animation-delay:{.4 + i * .8:.2f}s"><em>{e(x[0])}</em><div><b>{e(x[1])}</b><span>{e(x[2] if len(x) > 2 else "")}</span></div></div>' for i, x in enumerate(es.get('items', [])[:4]))
        return f'<h2 class="h t2 up">{rico(d("titulo"))}</h2><div class="steps">{it}</div>'
    if t == 'antesdespues':
        a = ''.join(f'<div class="left" style="animation-delay:{.5 + i * .35:.2f}s">❌ {e(x)}</div>' for i, x in enumerate(es.get('antes', [])[:4]))
        b = ''.join(f'<div class="right" style="animation-delay:{1.6 + i * .35:.2f}s">✅ {e(x)}</div>' for i, x in enumerate(es.get('despues', [])[:4]))
        return f'<h2 class="h t2 up">{rico(d("titulo"))}</h2><div class="ad"><div class="col antes pop" style="animation-delay:.3s"><h3 class="r">{e(es.get("antes_titulo", "Antes"))}</h3>{a}</div><div class="col despues pop" style="animation-delay:1.3s"><h3 class="v">{e(es.get("despues_titulo", "Con tu app"))}</h3>{b}</div></div>'
    if t == 'numero':
        return f'<h2 class="h t2 up">{rico(d("titulo"))}</h2><div class="big g pop" style="animation-delay:.4s"><span class="count" data-to="{int(es.get("numero", 0))}" data-pre="{e(d("prefijo"))}" data-at="0.5">0</span><small>{e(d("sufijo"))}</small></div><div class="lbl up" style="animation-delay:1s">{rico(d("etiqueta"))}</div>'
    if t == 'chips':
        ch = ''.join(f'<div class="up" style="animation-delay:{.8 + i * .3:.2f}s">{e(x)}</div>' for i, x in enumerate(es.get('chips', [])[:6]))
        return f'<h2 class="h t2 up">{rico(d("titulo"))}</h2><div class="emo pop float" style="font-size:240px;animation-delay:.3s,1s">{e(d("emoji") or "✨")}</div><div class="chips">{ch}</div>'
    if t == 'chat':
        ms = ''.join(f'<div class="msg {"k" if q == "k" else "c"} {"right" if q == "k" else "left"}" style="animation-delay:{.5 + i * .75:.2f}s">{e(x)}</div>' for i, (q, x) in enumerate(es.get('mensajes', [])[:5]))
        return f'<h2 class="h t2 up">{rico(d("titulo"))}</h2><div class="chat pop" style="animation-delay:.2s"><div class="top"><div class="av">🤖</div>{e(d("contacto") or "Asistente de tu negocio")}</div>{ms}</div>'
    if t == 'agenda':
        dias = ''.join(f'<div class="cd{" on" if dd == 18 else ""}{" off" if (dd + 5) % 7 in (0,) else ""}">{dd}</div>' for dd in range(1, 31))
        horas = ''.join(f'<div class="hs{" on" if h == "10:00 a. m." else ""}">{h}</div>' for h in ['9:00 a. m.', '10:00 a. m.', '11:30 a. m.', '3:00 p. m.'])
        return (f'<h2 class="h t2 up">{rico(d("titulo"))}</h2><div class="agcard pop" style="animation-delay:.3s"><div class="agh">📅 {e(d("mes") or "Noviembre")}</div>'
                f'<div class="agw"><span>L</span><span>M</span><span>M</span><span>J</span><span>V</span><span>S</span><span>D</span></div><div class="agg">{dias}</div></div>'
                f'<div class="aghs up" style="animation-delay:1.2s">{horas}</div>'
                f'<div class="mail pop" style="animation-delay:2.2s"><b>📩 {e(MARCA.get("correo") or "Confirmación")}</b><span>{e(d("mensaje") or "🎉 ¡Listo! Tu cita con " + MARCA["nombre"] + " está agendada")}</span></div>')
    if t == 'cta':
        bio = es.get('bio') or '👆 Toca el link de nuestro perfil'
        com = f'<div class="com up" style="animation-delay:1.4s">💬 o comenta "{e(palabra)}"</div>' if palabra and palabra.lower() not in (es.get('boton2') or '').lower() else ''
        return f'<div class="logo pop">{logo_html(True)}{e(MARCA["nombre"])}</div><div class="cta up" style="animation-delay:.4s">{e(es.get("boton") or MARCA.get("cta_boton") or "📅 Agenda tu reunión")}<em>{e(es.get("boton2") or MARCA.get("cta_boton2") or "GRATIS")}</em></div><div class="bio up" style="animation-delay:.9s">{e(bio)}</div>{com}'
    raise ValueError('Tipo de escena desconocido: ' + t)


def subtitulos(escenas, extra):
    hl = {w.lower().strip('¿?¡!.,:"') for w in RESALTAR + extra}
    caps = []
    for s in escenas:
        words = s['voz'].split(); chunks = []; cur = []
        for wd in words:
            cur.append(wd)
            if len(cur) >= 4 or (wd.endswith(('.', '?', ',', ':', '!')) and len(cur) >= 2):
                chunks.append(' '.join(cur)); cur = []
        if cur: chunks.append(' '.join(cur))
        tot = sum(len(c) for c in chunks); tt = s['voz_ini']
        for c in chunks:
            dd = s['voz_dur'] * len(c) / tot; caps.append((round(tt, 3), round(tt + dd, 3), c)); tt += dd
    fmt = lambda c: ' '.join(f'<b>{html.escape(w)}</b>' if w.lower().strip('¿?¡!.,:"') in hl else html.escape(w) for w in c.split())
    return caps, ''.join(f'<div class="cap" data-t0="{a}" data-t1="{b}"><span>{fmt(c)}</span></div>' for a, b, c in caps)


def armar_html(v, total, capdivs):
    def ajustar(h, dur):  # que todo aparezca antes del 55% de la escena
        ds = [float(x) for x in re.findall(r'animation-delay:([\d.]+)s', h)]
        k = min(1.0, dur * 0.55 / max(ds)) if ds and max(ds) > 0 else 1.0
        return re.sub(r'animation-delay:([\d.]+)s', lambda m: f'animation-delay:{float(m.group(1)) * k:.2f}s', h)
    def abajo(s):  # con la mascota al centro, el texto sube y ella queda debajo
        m = s.get('mascota')
        return ' conmasc' if isinstance(m, dict) and m.get('lado') == 'centro' else ''
    secs = ''.join(f'<section class="scene{abajo(s)}" data-start="{s["ini"]}" data-end="{s["fin"]}">{ajustar(escena_html(s, v["palabra"]), s["fin"] - s["ini"])}</section>\n' for s in v['escenas'])
    return f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="plantilla_video.css"></head><body>
<div class="bg"></div><div class="grid"></div><div class="bar" id="bar"></div><style>:root{{--c1:{MARCA['color1']};--c2:{MARCA['color2']};--bg:{MARCA['fondo']};--acento:{MARCA['acento']};--ctaem:{MARCA.get('cta_em') or MARCA['acento']}}}</style>
<div class="brand">{logo_html(False)}{e(MARCA['nombre'])}</div>
{secs}{capdivs}
<script>
const TOTAL={total};
window.setT=function(t){{
  document.querySelectorAll('.scene').forEach(s=>{{const st=+s.dataset.start,en=+s.dataset.end;s.style.setProperty('--dur',(en-st)+'s');s.style.visibility=(t>=st-0.01&&t<=en)?'visible':'hidden';}});
  document.getAnimations().forEach(a=>{{const el=a.effect&&a.effect.target;if(!el)return;const sc=el.closest('.scene');const st=sc?+sc.dataset.start:0;a.pause();a.currentTime=Math.max(0,(t-st)*1000);}});
  document.querySelectorAll('.cap').forEach(c=>{{c.style.visibility=(t>=+c.dataset.t0&&t<+c.dataset.t1)?'visible':'hidden';}});
  document.getElementById('bar').style.width=(t/TOTAL*100)+'%';
  document.querySelectorAll('.count').forEach(c=>{{const st=+c.closest('.scene').dataset.start+(+c.dataset.at);const p=Math.max(0,Math.min(1,(t-st)/1.1));c.textContent=c.dataset.pre+Math.round(p*(+c.dataset.to)).toLocaleString('en-US');}});
}};
</script></body></html>'''


# ---------- un video ----------
def hacer_video(v, voz, salida_dir):
    nombre = v['archivo']
    tmp = os.path.join(salida_dir, '_tmp_' + nombre); os.makedirs(tmp, exist_ok=True)
    t = 0.0
    for i, s in enumerate(v['escenas']):
        p = os.path.join(tmp, f's{i}.wav'); s['_wav'] = p
        dur = decir(voz, s['voz'], p)
        s['ini'] = round(t, 3); s['voz_ini'] = round(t + 0.12, 3); s['voz_dur'] = round(dur, 3)
        t += 0.12 + dur + (0.55 if s['tipo'] == 'cta' else 0.3)
        s['fin'] = round(t, 3)
    total = round(t + 0.6, 3); v['escenas'][-1]['fin'] = total
    # pista de voz
    sr = 44100; pista = np.zeros(int(total * sr) + sr, dtype=np.float32)
    for s in v['escenas']:
        with wave.open(s['_wav']) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        i = int(s['voz_ini'] * sr); pista[i:i + len(a)] += a[:len(pista) - i]
    voz_wav = os.path.join(tmp, 'voz.wav')
    with wave.open(voz_wav, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(pista, -1, 1) * 32767).astype(np.int16).tobytes())
    mus_wav = os.path.join(tmp, 'musica.wav'); musica(total, nombre, mus_wav)
    caps, capdivs = subtitulos(v['escenas'], v.get('resaltar', []))
    page = os.path.join(AQUI, f'_{nombre}.html')
    with open(page, 'w', encoding='utf-8') as f:
        f.write(armar_html(v, total, capdivs))
    mudo = os.path.join(tmp, 'mudo.mp4'); portada = os.path.join(salida_dir, nombre + '.jpg')
    sh('node', os.path.join(AQUI, 'render_video.cjs'), page, str(total), mudo, portada, str(min(1.4, v['escenas'][0]['fin'] - 0.3)))
    final = os.path.join(salida_dir, nombre + '.mp4')
    sh('ffmpeg', '-y', '-loglevel', 'error', '-i', mudo, '-i', voz_wav, '-i', mus_wav, '-filter_complex',
       '[2:a]volume=0.32[m];[1:a]asplit=2[v1][v2];[m][v2]sidechaincompress=threshold=0.04:ratio=6:attack=20:release=300[md];[v1][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.2[a]',
       '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-shortest', final)
    ts = lambda x: f'{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(round((x % 1) * 1000)) % 1000:03d}'
    with open(os.path.join(salida_dir, nombre + '.srt'), 'w', encoding='utf-8') as f:
        f.write(''.join(f'{k}\n{ts(a)} --> {ts(b)}\n{c}\n\n' for k, (a, b, c) in enumerate(caps, 1)))
    os.remove(page); subprocess.run(['rm', '-rf', tmp])
    print(f'✅ {nombre}.mp4  {total:.1f}s  {os.path.getsize(final) / 1e6:.1f} MB', flush=True)
    return {'archivo': nombre, 'duracion': total}


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
    RESALTAR.append(MARCA['nombre'].title())
    voz = asegurar_voz()
    vids = [v for i, v in enumerate(data['videos']) if solo is None or i == solo]
    # la voz se genera en serie (un solo modelo); el render de cuadros es lo más lento y va en paralelo
    with ThreadPoolExecutor(max_workers=3) as ex:
        res = list(ex.map(lambda v: hacer_video(v, voz, out), vids))
    print(json.dumps(res, ensure_ascii=False))


if __name__ == '__main__':
    main()
