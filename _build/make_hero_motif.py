# -*- coding: utf-8 -*-
"""Draw the hero background and favicon from the nested-networks sculpture.

Reads the sculpture's own primitive list (not a render) from
`Projects/3d-network-sculpture` and projects it to a simplified 2D line
drawing: the great circles of the outer shell, a thinned sample of the inner
struts, and a few nodes. Faint enough to sit behind text.

    python _build/make_hero_motif.py            # static/img/network.svg
    python _build/make_hero_motif.py --favicon  # static/img/favicon.svg
"""
import json
import math
import re
import sys
import argparse

sys.stdout.reconfigure(encoding='utf-8')

SRC = r'C:/Users/inhoc/Projects/3d-network-sculpture/prims_v3_150mm.json'
SLATE, COPPER = '#3f5a6b', '#9c6b3f'


def rot(p, az, el):
    """Azimuth about z, then elevation about the camera's x."""
    x, y, z = p
    ca, sa = math.cos(az), math.sin(az)
    x, y = x * ca - y * sa, x * sa + y * ca
    ce, se = math.cos(el), math.sin(el)
    y, z = y * ce - z * se, y * se + z * ce
    return x, y, z


def build(az_deg, el_deg, size, strut_keep, min_len, node_keep):
    prims = [p for p in json.load(open(SRC, encoding='utf-8')) if p.get('g') != 'base']
    az, el = math.radians(az_deg), math.radians(el_deg)
    centre = (0.0, 0.0, 81.0)

    def proj(p):
        q = rot((p[0] - centre[0], p[1] - centre[1], p[2] - centre[2]), az, el)
        return q[0], -q[2], q[1]          # screen x, screen y, depth

    pts, rings, struts, nodes = [], [], [], []

    for p in prims:
        if p['t'] == 'torus':
            u, v, c, R = p['u'], p['v'], p['c'], p['R']
            poly = []
            for k in range(181):
                a = k / 180 * 2 * math.pi
                w = [c[i] + R * (math.cos(a) * u[i] + math.sin(a) * v[i]) for i in range(3)]
                sx, sy, d = proj(w)
                poly.append((sx, sy))
                pts.append((sx, sy))
            rings.append(poly)
        elif p['t'] == 'cyl':
            ax, ay, ad = proj(p['a'])
            bx, by, bd = proj(p['b'])
            struts.append((math.dist(p['a'], p['b']), ax, ay, bx, by, (ad + bd) / 2))
            pts += [(ax, ay), (bx, by)]
        elif p['t'] == 'sphere':
            sx, sy, d = proj(p['c'])
            nodes.append((p['r'], sx, sy, d))
            pts.append((sx, sy))

    # thin the inner network: longest struts first, then an even sample of those
    struts.sort(key=lambda s: -s[0])
    struts = [s for s in struts if s[0] >= min_len]
    struts = struts[::max(1, round(len(struts) / strut_keep))][:strut_keep]
    nodes.sort(key=lambda n: -n[0])
    nodes = nodes[::max(1, round(len(nodes) / node_keep))][:node_keep]

    xs = [q[0] for q in pts]
    ys = [q[1] for q in pts]
    span = max(max(xs) - min(xs), max(ys) - min(ys))
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    k = (size * 0.94) / span

    def S(x, y):
        return size / 2 + (x - cx) * k, size / 2 + (y - cy) * k

    ds = [n[3] for n in nodes] + [s[5] for s in struts]
    dmin, dmax = min(ds), max(ds)

    def near(d):                          # 0 far … 1 near
        return 0.0 if dmax == dmin else (d - dmin) / (dmax - dmin)

    return {
        'size': size,
        'rings': [[S(x, y) for x, y in poly] for poly in rings],
        'struts': [(S(ax, ay), S(bx, by), near(d)) for _, ax, ay, bx, by, d in struts],
        'nodes': [(S(sx, sy), max(0.8, r * k * 0.5), near(d)) for r, sx, sy, d in nodes],
    }


def hero_svg(g):
    size = g['size']
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
           'width="%d" height="%d" role="presentation">' % (size, size, size, size),
           '<g stroke="%s" fill="none" stroke-linecap="round">' % SLATE]
    for (x1, y1), (x2, y2), n in g['struts']:
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                   'stroke-width="%.2f" opacity="%.3f"/>'
                   % (x1, y1, x2, y2, 0.65 + 0.55 * n, 0.09 + 0.19 * n))
    out.append('</g>')
    out.append('<g stroke="%s" fill="none" stroke-linejoin="round" '
               'stroke-linecap="round">' % COPPER)
    for poly in g['rings']:
        pth = ' '.join('%.1f,%.1f' % q for q in poly)
        out.append('<polyline points="%s" stroke-width="1.4" opacity="0.26"/>' % pth)
    out.append('</g>')
    out.append('<g fill="%s" stroke="none">' % SLATE)
    for (x, y), r, n in g['nodes']:
        out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" opacity="%.3f"/>'
                   % (x, y, r, 0.07 + 0.15 * n))
    out.append('</g>')
    out.append('</svg>')
    return '\n  '.join(out) + '\n'


def favicon_svg(g):
    """Six overlapping ellipses turn to mush at 16px. Keeping the three widest
    is no better: they are all near face-on and read as one wobbly circle. Take
    the most face-on ring for the outline and the two most edge-on ones for the
    crossing ellipses, which is the armillary figure the eye recognises small."""
    size = g['size']

    def area(poly):                       # shoelace: how face-on the ring is
        return abs(sum(poly[i][0] * poly[i - 1][1] - poly[i - 1][0] * poly[i][1]
                       for i in range(len(poly)))) / 2

    by_area = sorted(g['rings'], key=area)
    rings = [by_area[-1], by_area[0], by_area[1]]
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
           'width="%d" height="%d">' % (size, size, size, size),
           '<rect width="%d" height="%d" rx="6" fill="#1b2227"/>' % (size, size),
           '<g fill="none" stroke-linecap="round" stroke-linejoin="round">']
    for poly in rings:
        pth = ' '.join('%.2f,%.2f' % q for q in poly)
        out.append('<polyline points="%s" stroke="#c08a54" stroke-width="1.3"/>' % pth)
    for (x1, y1), (x2, y2), _ in g['struts']:
        out.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" '
                   'stroke="#9fb6c3" stroke-width="1.15"/>' % (x1, y1, x2, y2))
    out.append('</g><g fill="#eef3f6">')
    for (x, y), _, _ in g['nodes']:
        out.append('<circle cx="%.2f" cy="%.2f" r="1.3"/>' % (x, y))
    out.append('</g>')
    out.append('</svg>')
    return '\n  '.join(out) + '\n'


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--az', type=float, default=24)
    ap.add_argument('--el', type=float, default=14)
    ap.add_argument('--favicon', action='store_true')
    a = ap.parse_args()

    if a.favicon:
        g = build(a.az, a.el, 32, strut_keep=2, min_len=48.0, node_keep=2)
        svg, out = favicon_svg(g), 'static/img/favicon.svg'
    else:
        g = build(a.az, a.el, 820, strut_keep=175, min_len=9.0, node_keep=26)
        svg, out = hero_svg(g), 'static/img/network.svg'

    open(out, 'w', encoding='utf-8', newline='\n').write(svg)
    print('%s  %d bytes  az=%s el=%s' % (out, len(svg), a.az, a.el))
