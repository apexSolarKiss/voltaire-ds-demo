#!/usr/bin/env python3
"""Voltaire's identity, kept to one selection.

assets/identity.json names the identity parts and the ones this site shows. This
helper keeps the page and the repository artwork to that selection. The page never
runs it: the site stays static, and opening index.html needs nothing from here.

  python3 tools/identity.py check     check the page, its stylesheet and the artwork against identity.json
  python3 tools/identity.py build     write the banner master, voltaire-ds-demo-banner.svg, from identity.json
  python3 tools/identity.py render    export the banner master's PNGs with headless Chrome 109 or later, each
                                      stamped with the master's SHA-256 (set CHROME to the browser binary;
                                      the default is the macOS application path)

Standard library only. To change the selection: edit identity.json, the page's four
identity <img> paths and, if the lockup changes, the stylesheet's lockup numbers; run
`build` and `render`; then `check` until it passes.
"""
import hashlib, json, os, re, struct, subprocess, sys, tempfile, zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, 'assets', 'identity.json')
CHROME = os.environ.get('CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')


def read(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8', errors='replace') as f:
        return f.read()


STAMP = b'identity-master-sha256'
PAINT = {'class', 'fill', 'stroke', 'stroke-width', 'stroke-miterlimit', 'stroke-linejoin', 'stroke-linecap',
         'opacity', 'fill-opacity', 'stroke-opacity'}


def num(v):
    return f'{v:.4f}'.rstrip('0').rstrip('.')


def load():
    with open(MANIFEST, encoding='utf-8') as f:
        return json.load(f)


def selected(m):
    s = m['selection']
    return m['symbols'][s['symbol']], m['wordmarks'][s['wordmark']], m['lockups'][s['lockup']]


def view_box(svg):
    return [float(v) for v in re.search(r'<svg\b[^>]*\bviewBox="([^"]+)"', svg).group(1).split()]


def geometry(svg):
    """The drawn shapes with every attribute but their paint: what light and dark must share."""
    shapes = []
    for tag, attrs in re.findall(r'<(polyline|polygon|path|rect|circle|ellipse|line|g|use)\b([^>]*)>', svg):
        kept = sorted((k, v) for k, v in re.findall(r'([\w:-]+)="([^"]*)"', attrs) if k not in PAINT)
        shapes.append((tag, tuple(kept)))
    return shapes


def part(rel, scope):
    """A part's viewBox, its root paint attributes, its class styles scoped to #scope, and its shapes."""
    svg = read(rel)
    root = re.search(r'<svg\b([^>]*)>', svg).group(1)
    paint = ' '.join(re.findall(r'\b(?:fill|stroke)="[^"]*"', root))
    style = re.search(r'<style>(.*?)</style>', svg, re.S)
    rules = ''
    if style:
        for sel, body in re.findall(r'([^{}]+)\{([^}]*)\}', style.group(1)):
            scoped = ', '.join(f'#{scope} {s.strip()}' for s in sel.split(','))
            decls = ' '.join(d.strip() + ';' for d in body.split(';') if d.strip())
            rules += f'      {scoped} {{ {decls} }}\n'
    body = svg[svg.index('</defs>') + 7:] if '</defs>' in svg else svg[svg.index('>', svg.index('<svg')) + 1:]
    body = body[:body.rindex('</svg>')].strip('\n')
    return view_box(svg), paint, rules, body


def master(m):
    """The banner master: the selected lockup, in the artwork theme, on the design system's gradient."""
    sym, word, lock = selected(m)
    art = m['artwork']; theme = m['selection']['artwork_theme']
    W, H = art['size']; LW, LH = lock['box']
    k = W * art['lockup_width'] / LW
    x0, y0 = (W - LW * k) / 2, (H - LH * k) / 2
    q = (W + H) / 4   # CSS linear-gradient(45deg, a, b) on a W x H box: its ends sit (W+H)/4 from the centre on each axis
    a, b = art['ground'][theme]
    svb, spaint, srules, sbody = part(sym[theme], 'symbol')
    wvb, wpaint, wrules, wbody = part(word[theme], 'wordmark')

    def place(scope, box, vb, paint, body):
        x, y, w, h = box
        attrs = f' {paint}' if paint else ''
        return (f'  <svg id="{scope}" x="{num(x0 + x * k)}" y="{num(y0 + y * k)}" width="{num(w * k)}" height="{num(h * k)}" '
                f'viewBox="{" ".join(num(v) for v in vb)}"{attrs}>\n{body}\n  </svg>\n')
    styles = srules + wrules
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            f'  <!-- Built by tools/identity.py from assets/identity.json: the {m["selection"]["lockup"]} lockup in its '
            f'{theme}-theme parts,\n'
            f'       {sym[theme]} and {word[theme]}, on design-system-ASK\'s {theme} gradient.\n'
            f'       Edit identity.json or the parts, not this file. -->\n'
            f'  <defs>\n'
            f'    <linearGradient id="ground" gradientUnits="userSpaceOnUse" x1="{num(W / 2 - q)}" y1="{num(H / 2 + q)}" '
            f'x2="{num(W / 2 + q)}" y2="{num(H / 2 - q)}">\n'
            f'      <stop offset="0" stop-color="{a}"/>\n'
            f'      <stop offset="1" stop-color="{b}"/>\n'
            f'    </linearGradient>\n'
            + (f'    <style>\n{styles}    </style>\n' if styles else '') +
            f'  </defs>\n'
            f'  <rect width="{W}" height="{H}" fill="url(#ground)"/>\n'
            + place('symbol', lock['symbol'], svb, spaint, sbody)
            + place('wordmark', lock['wordmark'], wvb, wpaint, wbody)
            + '</svg>\n')


def png_info(rel):
    with open(os.path.join(ROOT, rel), 'rb') as f:
        data = f.read()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    w, h, depth, ctype = struct.unpack('>IIBB', data[16:26])
    chunks, text, i = [], {}, 8
    while i < len(data):
        n = struct.unpack('>I', data[i:i + 4])[0]; kind = data[i + 4:i + 8]; chunks.append(kind)
        if kind == b'tEXt':
            k, _, v = data[i + 8:i + 8 + n].partition(b'\x00'); text[k] = v
        i += 12 + n
    return w, h, ctype, chunks, text


def check():
    m = load(); bad = []
    s = m['selection']
    for kind, key in (('symbols', 'symbol'), ('wordmarks', 'wordmark'), ('lockups', 'lockup')):
        if s[key] not in m[kind]:
            bad.append(f'selection: {key} "{s[key]}" is not in {kind}')
    if bad:
        return bad
    sym, word, lock = selected(m)
    if lock.get('requires_initial') and not word.get('contains_initial'):
        bad.append(f'selection: lockup "{s["lockup"]}" needs a wordmark that contains the initial; "{s["wordmark"]}" does not')
    if s['artwork_theme'] not in m['artwork']['ground']:
        bad.append(f'selection: no ground for artwork theme "{s["artwork_theme"]}"')
    for kind, key in (('symbols', 'symbol'), ('wordmarks', 'wordmark')):
        for name, p in m[kind].items():
            if (name == s[key]) != (p.get('status') == 'current'):
                bad.append(f'{kind}.{name}: status "{p.get("status")}", but the selection {"names" if name == s[key] else "does not name"} it')
    if bad:
        return bad

    # every part exists, light and dark draw the same shapes, and each viewBox is the size the manifest gives
    paths = set()
    for kind in ('symbols', 'wordmarks'):
        for name, p in m[kind].items():
            for theme in ('light', 'dark'):
                paths.add(p[theme])
                if not os.path.isfile(os.path.join(ROOT, p[theme])):
                    bad.append(f'{kind}.{name}.{theme}: missing {p[theme]}')
            if all(os.path.isfile(os.path.join(ROOT, p[t])) for t in ('light', 'dark')):
                gl, gd = geometry(read(p['light'])), geometry(read(p['dark']))
                if not gl or gl != gd:
                    bad.append(f'{kind}.{name}: the light and dark files do not draw the same shapes')
                vl, vd = view_box(read(p['light'])), view_box(read(p['dark']))
                if vl != vd:
                    bad.append(f'{kind}.{name}: the light and dark files have different viewBoxes')
                for theme, vb in (('light', vl), ('dark', vd)):
                    if abs(vb[2] - p['size'][0]) > 0.01 or abs(vb[3] - p['size'][1]) > 0.01:
                        bad.append(f'{kind}.{name}.{theme}: viewBox {num(vb[2])} x {num(vb[3])}, identity.json gives {p["size"]}')
    on_disk = {f'assets/{f}' for f in os.listdir(os.path.join(ROOT, 'assets')) if re.match(r'voltaire-.*\.svg$', f)}
    for f in sorted(on_disk - paths):
        bad.append(f'{f}: an identity file identity.json does not list')

    # the page shows the selection
    page = read('index.html')
    mark = re.search(r'<a class="surface-mark"[^>]*>(.*?)</a>', page, re.S)
    if not mark:
        bad.append('index.html: no surface-mark link')
    else:
        for slot, p in (('symbol', sym), ('wordmark', word)):
            span = re.search(rf'<span class="surface-identity-{slot}">(.*?)</span>', mark.group(1), re.S)
            imgs = dict(re.findall(r'<img class="surface-mark-(light|dark)" src="([^"]+)"', span.group(1))) if span else {}
            for theme in ('light', 'dark'):
                if imgs.get(theme) != p[theme]:
                    bad.append(f'index.html: the {slot}\'s {theme} image is {imgs.get(theme)}, the selection is {p[theme]}')
            sizes = re.findall(r'width="(\d+)" height="(\d+)"', span.group(1)) if span else []
            want = (str(round(p['size'][0])), str(round(p['size'][1])))
            if not sizes or any(sz != want for sz in sizes):
                bad.append(f'index.html: the {slot} images\' width and height are {sizes}, the part is {want}')

    # the stylesheet composes the selected lockup
    css = read('styles/voltaire.css')
    bw, bh = lock['box']
    want = [f'--surface-identity-ratio: {num(bw)} / {num(bh)};']
    for slot in ('symbol', 'wordmark'):
        x, y, w, h = lock[slot]
        def frac(v, d):
            return '0%' if v == 0 else '100%' if v == d else f'calc({num(v)} / {num(d)} * 100%)'
        want += [f'--surface-identity-{slot}-x: {frac(x, bw)};', f'--surface-identity-{slot}-y: {frac(y, bh)};',
                 f'--surface-identity-{slot}-w: {frac(w, bw)};', f'--surface-identity-{slot}-h: {frac(h, bh)};']
    for decl in want:
        if css.count(decl) != 1:
            bad.append(f'styles/voltaire.css: expected once: {decl}')

    # no text file names an identity file the manifest does not list, with or without its folder
    listed = {os.path.basename(x) for x in paths}
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', '_dsa-tokens', '_dsa-surface', 'figures', 'licenses')]
        for f in files:
            if f.endswith(('.html', '.md', '.css', '.svg', '.js', '.json', '.py')) or f in ('NOTICE', 'LICENSE'):
                rel = os.path.relpath(os.path.join(dirpath, f), ROOT)
                for ref in set(re.findall(r'voltaire-(?:symbol|wordmark)-[\w-]+\.svg', read(rel))):
                    if ref not in listed:
                        bad.append(f'{rel}: names {ref}, which identity.json does not list')

    # the artwork is built from the selection, at the sizes the manifest gives
    art = m['artwork']
    try:
        if read(art['master']) != master(m):
            bad.append(f'{art["master"]}: not what `build` writes from identity.json; run `python3 tools/identity.py build`')
    except FileNotFoundError as e:
        bad.append(f'{art["master"]}: cannot be checked: {os.path.relpath(e.filename, ROOT)} is missing')
    stamp = hashlib.sha256(open(os.path.join(ROOT, art['master']), 'rb').read()).hexdigest().encode() \
        if os.path.isfile(os.path.join(ROOT, art['master'])) else None
    for e in art['exports']:
        info = png_info(e['path']) if os.path.isfile(os.path.join(ROOT, e['path'])) else None
        if not info:
            bad.append(f'{e["path"]}: missing or not a PNG')
            continue
        w, h, ctype, chunks, text = info
        if [w, h] != e['size'] or ctype != 2:
            bad.append(f'{e["path"]}: {w} x {h}, color type {ctype}; expected {e["size"][0]} x {e["size"][1]} RGB')
        if b'sRGB' not in chunks and b'iCCP' not in chunks:
            bad.append(f'{e["path"]}: declares no sRGB color space')
        if text.get(STAMP) != stamp:
            bad.append(f'{e["path"]}: not exported from the current banner master; run `python3 tools/identity.py render`')
    return bad


def build():
    m = load()
    with open(os.path.join(ROOT, m['artwork']['master']), 'w', encoding='utf-8') as f:
        f.write(master(m))
    print('wrote', m['artwork']['master'])


def with_srgb(data, stamp):
    """The PNG with an sRGB chunk and the master's stamp after IHDR, no other color-space chunk; pixels untouched."""
    out, i = [data[:8]], 8
    while i < len(data):
        n = struct.unpack('>I', data[i:i + 4])[0]; kind = data[i + 4:i + 8]; chunk = data[i:i + 12 + n]; i += 12 + n
        if kind in (b'sRGB', b'iCCP', b'gAMA', b'cHRM', b'tEXt'):
            continue
        out.append(chunk)
        if kind == b'IHDR':
            for body in (b'sRGB' + b'\x00', b'tEXt' + STAMP + b'\x00' + stamp):
                out.append(struct.pack('>I', len(body) - 4) + body + struct.pack('>I', zlib.crc32(body)))
    return b''.join(out)


def render():
    m = load(); art = m['artwork']; W, H = art['size']
    svg = read(art['master'])
    stamp = hashlib.sha256(open(os.path.join(ROOT, art['master']), 'rb').read()).hexdigest().encode()
    with tempfile.TemporaryDirectory() as tmp:
        for e in art['exports']:
            ew, eh = e['size']
            if e.get('crop') == 'full-width-center':
                ch = W * eh / ew; vb = f'0 {num((H - ch) / 2)} {W} {num(ch)}'
            else:
                vb = f'0 0 {W} {H}'
            s = re.sub(r'<svg ([^>]*?)width="\d+" height="\d+" viewBox="[^"]+">',
                       lambda mm: f'<svg {mm.group(1)}width="{ew}" height="{eh}" viewBox="{vb}">', svg, count=1)
            with open(os.path.join(tmp, 'art.svg'), 'w', encoding='utf-8') as f:
                f.write(s)
            with open(os.path.join(tmp, 'art.html'), 'w', encoding='utf-8') as f:
                f.write(f'<!DOCTYPE html><html><head><style>html,body{{margin:0;background:#000}}img{{display:block}}</style>'
                        f'</head><body><img src="art.svg" width="{ew}" height="{eh}"></body></html>')
            shot = os.path.join(tmp, 'shot.png')
            subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
                            '--force-color-profile=srgb', '--force-device-scale-factor=1', f'--user-data-dir={tmp}/profile',
                            f'--window-size={ew},{eh}', f'--screenshot={shot}', 'file://' + os.path.join(tmp, 'art.html')],
                           check=True, capture_output=True)
            with open(shot, 'rb') as f:
                data = with_srgb(f.read(), stamp)
            with open(os.path.join(ROOT, e['path']), 'wb') as f:
                f.write(data)
            print('wrote', e['path'])


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if cmd == 'build':
        build()
    elif cmd == 'render':
        render()
    elif cmd == 'check':
        problems = check()
        for p in problems:
            print('FAIL', p)
        print('identity: ' + ('PASS' if not problems else f'{len(problems)} problem(s)'))
        sys.exit(1 if problems else 0)
    else:
        sys.exit(__doc__)
