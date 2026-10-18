"""Rebuild the temporary, self-contained SVG sequence for /experience.

Run with Python 3. No third-party packages, network access, or source images are
required. Replace the generated frame files with a video-derived sequence later.
"""

from math import cos, pi, sin
from pathlib import Path
import xml.etree.ElementTree as ET


OUTPUT = Path(__file__).resolve().parents[1] / "src/main/resources/static/experience/frames"
FRAME_COUNT = 60


def smooth(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def number(value):
    return f"{value:.2f}".rstrip("0").rstrip(".")


def point(value):
    return f"{number(value[0])},{number(value[1])}"


def polygon(points, attributes):
    return f'<polygon points="{" ".join(point(p) for p in points)}" {attributes}/>'


def frame(progress):
    # A very gentle camera orbit keeps the transformation continuous in reverse.
    angle = -0.08 + progress * 0.14

    def project(x, y, z):
        rx = x * cos(angle) - z * sin(angle)
        rz = x * sin(angle) + z * cos(angle)
        return (1120 + (rx - rz) * 0.86, 674 + (rx + rz) * 0.43 - y)

    def line(a, b, attributes):
        return f'<path d="M{point(a)} L{point(b)}" {attributes}/>'

    def cube(x, y, z, size, opacity, primary=False):
        half = size / 2
        corners = {
            "a": project(x-half, y+half, z-half),
            "b": project(x+half, y+half, z-half),
            "c": project(x+half, y+half, z+half),
            "d": project(x-half, y+half, z+half),
            "e": project(x-half, y-half, z-half),
            "f": project(x+half, y-half, z-half),
            "g": project(x+half, y-half, z+half),
            "h": project(x-half, y-half, z+half),
        }
        c = corners
        parts = [f'<g opacity="{number(opacity)}">']
        # The soft silhouette and nested core give the vector a glass volume.
        glow = [c[k] for k in "abcdhgfe"]
        parts.append(polygon(glow, 'fill="#ffe84b" opacity=".09" filter="url(#bloom)"'))
        inner = size * (0.41 if primary else 0.31)
        ih = inner / 2
        core = [project(x-ih, y+ih, z-ih), project(x+ih, y+ih, z-ih),
                project(x+ih, y+ih, z+ih), project(x-ih, y+ih, z+ih)]
        parts.append(polygon(core, 'fill="#fff9ad" opacity=".9" filter="url(#soft)"'))
        parts.append(polygon([core[3], core[2], project(x+ih, y-ih, z+ih), project(x-ih, y-ih, z+ih)],
                             'fill="url(#coreFront)"'))
        parts.append(polygon([core[1], core[2], project(x+ih, y-ih, z+ih), project(x+ih, y-ih, z-ih)],
                             'fill="#e5b900" opacity=".85"'))
        parts.append(polygon(core, 'fill="#fff6a1" opacity=".96"'))
        # Back edges remain visible through the tinted shell.
        parts.append(line(c["a"], c["e"], 'stroke="#e7d77d" stroke-width=".8" opacity=".25"'))
        parts.append(line(c["e"], c["h"], 'stroke="#e7d77d" stroke-width=".8" opacity=".2"'))
        parts.append(line(c["e"], c["f"], 'stroke="#e7d77d" stroke-width=".8" opacity=".2"'))
        parts.append(polygon([c[k] for k in "dcgh"], 'fill="url(#glassFront)" stroke="#ffe879" stroke-opacity=".42" stroke-width="1.2" stroke-linejoin="round"'))
        parts.append(polygon([c[k] for k in "bcgf"], 'fill="url(#glassSide)" stroke="#e3cd70" stroke-opacity=".34" stroke-width="1.2" stroke-linejoin="round"'))
        parts.append(polygon([c[k] for k in "abcd"], 'fill="url(#glassTop)" stroke="#fff4b2" stroke-opacity=".8" stroke-width="1.4" stroke-linejoin="round"'))
        # A narrow edge bevel and highlight make the shell feel manufactured.
        parts.append(line(c["d"], c["c"], 'stroke="#fff5be" stroke-width="2" opacity=".85"'))
        parts.append(line(c["c"], c["g"], 'stroke="#ffe357" stroke-width="1.7" opacity=".8"'))
        inset = size * 0.11
        for step in (0.18, 0.28, 0.38):
            a = project(x-half+inset, y-half+size*step, z+half+0.15)
            b = project(x+half-inset, y-half+size*step, z+half+0.15)
            parts.append(line(a, b, 'stroke="#fff4ac" stroke-width=".7" opacity=".18"'))
        # Tiny status light is an abstract visual, not a real health indicator.
        light = project(x+half-inset, y-half+size*0.76, z+half+0.5)
        parts.append(f'<circle cx="{number(light[0])}" cy="{number(light[1])}" r="2.2" fill="#fff6b0"/>')
        parts.append('</g>')
        return "".join(parts)

    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000">',
             '<defs>',
             '<radialGradient id="atmosphere"><stop stop-color="#b29d37" stop-opacity=".13"/><stop offset="1" stop-color="#0b0f13" stop-opacity="0"/></radialGradient>',
             '<radialGradient id="floorGlow"><stop stop-color="#e7c528" stop-opacity=".16"/><stop offset=".55" stop-color="#baa52c" stop-opacity=".045"/><stop offset="1" stop-color="#0b0f13" stop-opacity="0"/></radialGradient>',
             '<linearGradient id="glassTop" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fffbd5" stop-opacity=".42"/><stop offset=".5" stop-color="#e9d35e" stop-opacity=".14"/><stop offset="1" stop-color="#a99d53" stop-opacity=".28"/></linearGradient>',
             '<linearGradient id="glassFront" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#f8e46b" stop-opacity=".2"/><stop offset=".48" stop-color="#9da9a4" stop-opacity=".07"/><stop offset="1" stop-color="#e0c83e" stop-opacity=".23"/></linearGradient>',
             '<linearGradient id="glassSide" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#e4d678" stop-opacity=".11"/><stop offset="1" stop-color="#19242b" stop-opacity=".77"/></linearGradient>',
             '<linearGradient id="coreFront" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#ffe66b"/><stop offset="1" stop-color="#b58c00"/></linearGradient>',
             '<linearGradient id="lineFade"><stop stop-color="#e2ce60" stop-opacity="0"/><stop offset=".5" stop-color="#e2ce60" stop-opacity=".24"/><stop offset="1" stop-color="#e2ce60" stop-opacity="0"/></linearGradient>',
             '<filter id="bloom" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="18"/></filter>',
             '<filter id="soft" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="5"/></filter>',
             '</defs>',
             '<rect width="1600" height="1000" fill="#0b0f13"/>',
             '<ellipse cx="1150" cy="480" rx="650" ry="510" fill="url(#atmosphere)"/>',
             '<ellipse cx="1130" cy="705" rx="480" ry="230" fill="url(#floorGlow)"/>']

    # Ground lattice is restricted to the visual side of the composition.
    parts.append('<g stroke="#b2b09b" stroke-width=".7" opacity=".07">')
    for distance in range(-400, 401, 80):
        parts.append(line(project(distance, -15, -400), project(distance, -15, 400), ''))
        parts.append(line(project(-400, -15, distance), project(400, -15, distance), ''))
    parts.append('</g>')
    parts.append('<ellipse cx="1120" cy="696" rx="300" ry="88" fill="none" stroke="#c8bb72" stroke-width=".8" opacity=".13"/>')
    parts.append('<ellipse cx="1120" cy="696" rx="220" ry="64" fill="none" stroke="#e2ca4c" stroke-width=".7" opacity=".11" stroke-dasharray="2 12"/>')
    parts.append('<path d="M630 818 H1530" stroke="url(#lineFade)" stroke-width=".8"/>')

    expansion = smooth(progress)
    center = (0, 205 + sin(progress*pi) * 10, 0)
    nodes = [(center[0], center[1], center[2], 135-27*expansion, 1, True)]
    destinations = [
        (170, 126, -20, 78, .02),
        (-165, 124, -12, 82, .05),
        (14, 132, 183, 79, .12),
        (18, 256, -185, 84, .16),
        (176, 260, 144, 71, .34),
        (-180, 250, -147, 75, .39),
        (-10, 381, -8, 64, .49),
    ]
    connections = []
    for index, (dx, dy, dz, size, start) in enumerate(destinations):
        arrival = smooth((progress-start)/(.43 if index < 4 else .45))
        if arrival <= 0:
            continue
        x = dx*arrival
        y = center[1] + (dy-center[1])*arrival + sin(arrival*pi)*(25+index*3)
        z = dz*arrival
        opacity = smooth(arrival*2.5)
        nodes.append((x, y, z, size*(.45+.55*arrival), opacity, False))
        connections.append((center, (x,y,z), arrival, index))

    # Connections sit behind the floating modules, with a moving signal dot.
    parts.append('<g fill="none" stroke-linecap="round">')
    for a, b, arrival, index in connections:
        pa, pb = project(*a), project(*b)
        path = f'M{point(pa)} L{point(pb)}'
        opacity = .42*smooth((arrival-.08)/.7)
        parts.append(f'<path d="{path}" stroke="#f6d838" stroke-width="6" opacity="{number(opacity*.3)}" filter="url(#soft)"/>')
        parts.append(f'<path d="{path}" stroke="#daca70" stroke-width="1.1" opacity="{number(opacity)}"/>')
        along = (progress*1.8+index*.18) % 1
        particle = (pa[0]+(pb[0]-pa[0])*along, pa[1]+(pb[1]-pa[1])*along)
        parts.append(f'<circle cx="{number(particle[0])}" cy="{number(particle[1])}" r="2" fill="#ffe97d" stroke="none" opacity="{number(opacity)}"/>')
    parts.append('</g>')

    # Sort the glass modules by projected depth, so overlap remains consistent.
    nodes.sort(key=lambda n: n[0]+n[2]-n[1]*.35)
    for x,y,z,size,opacity,primary in nodes:
        parts.append(cube(x,y,z,size,opacity,primary))

    # Small atmospheric points add scale without competing with the headline.
    parts.append('<g fill="#ffed9a">')
    for index in range(15):
        x = 770 + ((index*137) % 700)
        y = 220 + ((index*89) % 560) - progress*(10+index%4*7)
        radius = .7 if index%3 else 1.3
        opacity = .08 + (index%4)*.03
        parts.append(f'<circle cx="{x}" cy="{number(y)}" r="{radius}" opacity="{number(opacity)}"/>')
    parts.extend(['</g>', '</svg>'])
    return "".join(parts)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for index in range(FRAME_COUNT):
        svg = frame(index/(FRAME_COUNT-1))
        ET.fromstring(svg)
        (OUTPUT / f"frame-{index:03}.svg").write_text(svg, encoding="utf-8")
    (OUTPUT / "poster.svg").write_text(frame(0), encoding="utf-8")
    files = list(OUTPUT.glob("*.svg"))
    print(f"Generated {len(files)} SVG images, {sum(p.stat().st_size for p in files):,} bytes total.")


if __name__ == "__main__":
    main()
