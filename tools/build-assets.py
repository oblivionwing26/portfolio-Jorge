#!/usr/bin/env python3
"""Prepara las texturas del juego a partir de las fuentes CC0 de Poly Haven.

Uso:  python3 tools/build-assets.py <carpeta-con-las-descargas> [assets/tex]

La carpeta de entrada contiene los mapas a 1k con el nombre «<asset>__<mapa>.jpg|png»
(por ejemplo «leafy_grass__Diffuse.jpg», «fir_tree_01__twig_alpha.png»), tal como los
descarga la API de Poly Haven (https://api.polyhaven.com/files/<asset>).

Salida (WebP):
  t_*.webp  detalle de superficie normalizado (media ≈ 0,5 por canal). El juego lo usa
            como multiplicador sobre el color pintado del terreno o de la arquitectura,
            de modo que conserva la paleta del valle y añade grano, piedras y vetas reales.
  f_*.webp  tarjetas de follaje RGBA (ramas de abeto, hojas, matas de hierba, helechos)
            con el color extendido bajo las zonas transparentes para evitar halos oscuros.
  f_blossom.webp  racimo de flores de cerezo dibujado por código (sin fuente externa).
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat

SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else 'assets/tex'
os.makedirs(OUT, exist_ok=True)


def src(name):
    for ext in ('jpg', 'png'):
        p = os.path.join(SRC, f'{name}.{ext}')
        if os.path.exists(p):
            return Image.open(p)
    raise FileNotFoundError(name)


def save(im, name, q=82):
    p = os.path.join(OUT, name + '.webp')
    im.save(p, 'WEBP', quality=q, method=6)
    print(f'{name:14s} {im.size[0]}x{im.size[1]} {os.path.getsize(p) // 1024} KB')


# ---------- detalle de superficie ----------
DETAIL = {
    't_grass': ('leafy_grass__Diffuse', 1.7),
    't_forest': ('forest_ground_04__Diffuse', 1.0),
    't_path': ('stony_dirt_path__Diffuse', 1.0),
    't_rock': ('rock_face__Diffuse', 1.0),
    't_moss': ('mossy_rock__Diffuse', 1.0),
    't_pebble': ('river_small_rocks__Diffuse', 1.0),
    't_snow': ('snow_02__Diffuse', .8),
    't_wood': ('japanese_cedar_planks__Diffuse', 1.0, 0),
    't_plaster': ('white_plaster_rough_01__Diffuse', 1.4),
    't_roof': ('grey_roof_tiles__Diffuse', 1.0),
    't_stone': ('japanese_stone_wall__Diffuse', 1.0),
    't_thatch': ('thatch_roof_angled__Diffuse', 1.0),
    't_bark': ('sakura_bark__Diffuse', 1.0),
    't_pine': ('pine_bark__Diffuse', 1.0),
}
for out, spec in DETAIL.items():
    name, gain, chroma = (spec + (.35,))[:3]
    # detalle sobre todo de luminancia, con un 35 % de la variación de color original
    a = np.asarray(src(name).convert('RGB').resize((512, 512), Image.LANCZOS)).astype(np.float32) / 255
    lum = a @ np.array([.3, .59, .11], np.float32)
    l = lum / max(lum.mean(), 1e-3)
    c = a / np.maximum(a.reshape(-1, 3).mean(0), 1e-3)
    d = l[..., None] + (c - l[..., None]) * chroma
    d = 1 + (d - 1) * gain
    save(Image.fromarray(np.clip(d * .5 * 255, 0, 255).astype(np.uint8), 'RGB'), out, 80)


# ---------- follaje ----------
def bleed(rgba, it=24):
    """Extiende el color de los píxeles opacos bajo los transparentes (sin halos en los mipmaps)."""
    arr = np.asarray(rgba).astype(np.float32)
    rgb, a = arr[..., :3], arr[..., 3]
    m = (a > 8).astype(np.float32)
    col = rgb * m[..., None]
    for _ in range(it):
        def blur(x):
            return (x + np.roll(x, 1, 0) + np.roll(x, -1, 0) + np.roll(x, 1, 1) + np.roll(x, -1, 1)) / 5
        c2, m2 = blur(col), blur(m)
        fill = (m == 0) & (m2 > 1e-3)
        col[fill] = c2[fill] / m2[fill][..., None]
        m = np.maximum(m, (m2 > 1e-3).astype(np.float32))
        col = col * (m[..., None] > 0)
    out = np.dstack([np.clip(col, 0, 255), a]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def card(diff, alpha, box, size, tint=None):
    d, a = src(diff).convert('RGB'), src(alpha).convert('L')
    W, H = d.size
    b = (int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H))
    im = d.crop(b); al = a.crop(b)
    if tint:
        im = Image.blend(im, Image.new('RGB', im.size, tint[0]), tint[1])
    im = im.convert('RGBA'); im.putalpha(al)
    return im.resize(size, Image.LANCZOS)


def atlas(cards, cell):
    out = Image.new('RGBA', (cell[0] * len(cards), cell[1]), (0, 0, 0, 0))
    for i, c in enumerate(cards):
        out.paste(c, (i * cell[0], 0))
    return out


fir = atlas([card('fir_tree_01__twig_diff', 'fir_tree_01__twig_alpha', (.30, .40, .64, .87), (256, 256)),
             card('fir_tree_01__twig_diff', 'fir_tree_01__twig_alpha', (.62, .42, .99, .87), (256, 256))], (256, 256))
save(bleed(fir), 'f_fir', 84)
# racimos de hojas: se estampan hojas reales sueltas (arbusto shrub_01) giradas alrededor del centro
LEAVES = [(.42, .03, .63, .41), (.73, .11, .93, .37), (.73, .40, .97, .74), (.23, .41, .49, .73)]
def cluster(seed, S=512, n=110, autumn=0):
    rnd = random.Random(seed); out = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    srcs = [card('shrub_01__Diffuse', 'shrub_01__Alpha', b, (160, 200)) for b in LEAVES]
    for i in range(n):
        r = (rnd.random() ** .55) * .4 * S; a = rnd.uniform(0, math.tau)
        x, y = S / 2 + math.cos(a) * r, S / 2 + math.sin(a) * r
        lf = srcs[rnd.randrange(len(srcs))]
        k = rnd.uniform(.32, .5) * (1.15 - r / S)
        lf = lf.resize((int(lf.size[0] * k), int(lf.size[1] * k)), Image.LANCZOS).rotate(math.degrees(-a) - 90 + rnd.uniform(-35, 35), expand=True, resample=Image.BICUBIC)
        shade = rnd.uniform(.7, 1.08) * (1 - .25 * (i / n < .4))
        rgb = lf.convert('RGB').point(lambda v, s=shade: min(255, int(v * s)))
        lf2 = rgb.convert('RGBA'); lf2.putalpha(lf.getchannel('A'))
        out.alpha_composite(lf2, (int(x - lf.size[0] / 2), int(y - lf.size[1] / 2)))
    return out
save(bleed(atlas([cluster(3), cluster(9)], (512, 512)).resize((512, 256), Image.LANCZOS)), 'f_leaf', 84)
grass = atlas([card('grass_medium_01__Diffuse', 'grass_medium_01__Alpha', (.18, .752, .505, .945), (256, 176)),
               card('grass_medium_01__Diffuse', 'grass_medium_01__Alpha', (.56, .752, .83, .887), (256, 176))], (256, 176))
save(bleed(grass), 'f_grass', 84)
fern = atlas([card('fern_02__Diffuse', 'fern_02__Alpha', (x, .09, x + .16, .97), (96, 384)) for x in (.065, .31, .72)], (96, 384))
save(bleed(fern), 'f_fern', 84)


# ---------- racimo de flores de cerezo (dibujado) ----------
def blossom(seed=7, S=1024):
    rnd = random.Random(seed)
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    cx, cy = S / 2, S / 2
    # ramitas
    for _ in range(7):
        a = rnd.uniform(0, math.tau); L = rnd.uniform(.25, .45) * S
        x0, y0 = cx + rnd.uniform(-.06, .06) * S, cy + rnd.uniform(-.06, .06) * S
        pts = [(x0, y0)]
        for k in range(1, 5):
            a += rnd.uniform(-.35, .35)
            pts.append((pts[-1][0] + math.cos(a) * L / 4, pts[-1][1] + math.sin(a) * L / 4))
        dr.line(pts, fill=(78, 52, 46, 255), width=int(S * .012), joint='curve')
    # base rellena (masa de flores lejanas): la silueta queda sólida y el contorno lo marcan las flores
    for _ in range(26):
        r = (rnd.random() ** .7) * .3 * S; a = rnd.uniform(0, math.tau); x, y = cx + math.cos(a) * r, cy + math.sin(a) * r; R = rnd.uniform(.07, .12) * S
        t = rnd.random(); dr.ellipse((x - R, y - R * .85, x + R, y + R * .85), fill=(int(238 + 12 * t), int(176 + 30 * t), int(196 + 24 * t), 255))
    flowers = []
    for _ in range(64):
        r = (rnd.random() ** .75) * .4 * S; a = rnd.uniform(0, math.tau)
        flowers.append((cx + math.cos(a) * r, cy + math.sin(a) * r, rnd.uniform(.042, .07) * S, rnd.uniform(0, math.tau), rnd.random()))
    flowers.sort(key=lambda f: f[4])
    for x, y, R, rot, sh in flowers:
        base = (255, int(214 + 26 * sh), int(226 + 20 * sh))
        deep = (236, int(146 + 40 * sh), int(176 + 30 * sh))
        for p in range(5):
            pa = rot + p * math.tau / 5
            px, py = x + math.cos(pa) * R * .55, y + math.sin(pa) * R * .55
            # pétalo: dos elipses (oscura detrás, clara encima) con muesca
            for k, col in ((1.0, deep), (.82, base)):
                rx, ry = R * .52 * k, R * .38 * k
                poly = []
                for t in range(24):
                    u = t / 24 * math.tau
                    ex, ey = math.cos(u) * rx, math.sin(u) * ry
                    if abs(u - 0) < .25 or abs(u - math.tau) < .25:
                        ex *= .78
                    poly.append((px + ex * math.cos(pa) - ey * math.sin(pa), py + ex * math.sin(pa) + ey * math.cos(pa)))
                dr.polygon(poly, fill=col + (255,))
        dr.ellipse((x - R * .18, y - R * .18, x + R * .18, y + R * .18), fill=(204, 74, 108, 255))
        for s in range(6):
            sa = rot + s * math.tau / 6
            dr.line((x, y, x + math.cos(sa) * R * .3, y + math.sin(sa) * R * .3), fill=(250, 214, 120, 255), width=max(1, int(S * .003)))
    # capullos
    for _ in range(14):
        r = rnd.uniform(.3, .46) * S; a = rnd.uniform(0, math.tau); x, y = cx + math.cos(a) * r, cy + math.sin(a) * r; R = S * .016
        dr.ellipse((x - R, y - R * 1.3, x + R, y + R * 1.3), fill=(226, 108, 140, 255))
    # la máscara recorta en círculo blando para que la tarjeta no tenga bordes rectos
    return im.resize((512, 512), Image.LANCZOS)


save(bleed(blossom()), 'f_blossom', 86)


# ---------- mata de hierba estilizada (dibujada): hojas curvas con degradado de la base a la punta ----------
def grass_tex(seed=4, W=512, Hh=512):
    rnd = random.Random(seed); S = 2
    im = Image.new('RGBA', (W * S, Hh * S), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    for i in range(90):
        x0 = rnd.uniform(.08, .92) * W * S; h = rnd.uniform(.45, .98) * Hh * S; w = rnd.uniform(.012, .026) * W * S
        bend = rnd.uniform(-.25, .25) * h; t0 = rnd.random()
        base = (int(46 + 20 * t0), int(84 + 24 * t0), int(34 + 10 * t0)); tip = (int(150 + 50 * t0), int(190 + 30 * t0), int(84 + 30 * t0))
        N = 14
        for k in range(N):
            a, b = k / N, (k + 1) / N
            def P(t, side):
                x = x0 + bend * t * t + side * w * (1 - t) ** .8
                return (x, Hh * S - t * h)
            col = tuple(int(base[c] + (tip[c] - base[c]) * (a ** .8)) for c in range(3)) + (255,)
            dr.polygon([P(a, -1), P(a, 1), P(b, 1), P(b, -1)], fill=col)
    return im.resize((W, Hh), Image.LANCZOS)


save(bleed(grass_tex()), 'f_blades', 84)


# ---------- racimos de hojas dibujados: arce japonés, ginkgo y sauce ----------
def leaf_shape(kind, R, rot):
    """Polígono de una hoja centrada en (0,0) apuntando hacia arriba, girada «rot»."""
    pts = []
    if kind == 'maple':  # hoja palmeada de 7 lóbulos
        for t in range(140):
            u = t / 140 * math.tau
            lobes = abs(math.cos(u * 3.5)) ** .6
            r = R * (.38 + .62 * lobes) * (1 - .25 * max(0, -math.sin(u)))
            pts.append((math.sin(u) * r, -math.cos(u) * r))
    elif kind == 'ginkgo':  # abanico con muesca central
        for t in range(60):
            u = -1.05 + 2.1 * t / 59
            notch = 1 - .22 * math.exp(-(u / .12) ** 2)
            pts.append((math.sin(u) * R * notch, -math.cos(u) * R * notch))
        pts.append((R * .06, R * .1)); pts.append((-R * .06, R * .1))
    else:  # hoja lanceolada (sauce)
        for t in range(40):
            u = t / 39 * math.tau
            pts.append((math.sin(u) * R * .18, -math.cos(u) * R))
    c, s_ = math.cos(rot), math.sin(rot)
    return [(x * c - y * s_, x * s_ + y * c) for x, y in pts]


def leaf_cluster(kind, cols, seed, S=1024, n=150):
    rnd = random.Random(seed); im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    cx = cy = S / 2
    for i in range(n):
        r = (rnd.random() ** .7) * .42 * S; a = rnd.uniform(0, math.tau)
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        R = S * rnd.uniform(.045, .07) * (1.1 - r / S)
        col = cols[rnd.randrange(len(cols))]; sh = rnd.uniform(.72, 1.08) * (.8 + .25 * (i / n))
        fill = tuple(min(255, int(c * sh)) for c in col) + (255,)
        poly = [(x + px, y + py) for px, py in leaf_shape(kind, R, a + math.pi / 2 + rnd.uniform(-.6, .6))]
        dr.polygon(poly, fill=fill)
        vein = tuple(min(255, int(c * sh * 1.18)) for c in col) + (255,)
        dr.line([(x, y), (x + math.cos(a) * R * .8, y + math.sin(a) * R * .8)], fill=vein, width=max(1, S // 400))
    return im.resize((512, 512), Image.LANCZOS)


save(bleed(leaf_cluster('maple', [(214, 58, 38), (232, 92, 40), (190, 40, 46), (244, 132, 52), (160, 32, 40)], 11)), 'f_maple', 86)
save(bleed(leaf_cluster('ginkgo', [(246, 196, 60), (236, 176, 44), (250, 214, 96), (214, 160, 40)], 12)), 'f_ginkgo', 86)


def willow(seed=5, W=256, Hh=1024):
    rnd = random.Random(seed); S = 2; im = Image.new('RGBA', (W * S, Hh * S), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    for k in range(9):
        x0 = rnd.uniform(.15, .85) * W * S; L = rnd.uniform(.7, 1.0) * Hh * S; sway = rnd.uniform(-.08, .08) * W * S
        dr.line([(x0, 0), (x0 + sway, L)], fill=(92, 104, 52, 255), width=2)
        for j in range(int(L / (14 * S))):
            t = j * 14 * S / L; x, y = x0 + sway * t, t * L
            for sd in (-1, 1):
                g = rnd.uniform(.8, 1.1); col = (int(120 * g), int(168 * g), int(70 * g), 255)
                poly = [(x + px, y + py) for px, py in leaf_shape('willow', 13 * S, sd * rnd.uniform(.5, .9) + math.pi)]
                dr.polygon(poly, fill=col)
    return im.resize((W, Hh), Image.LANCZOS)


save(bleed(willow()), 'f_willow', 86)
