"""Generate a small ASCII STL of a 3D neural network (nodes + connections).

GitHub renders ```stl fenced code blocks as an interactive 3D viewer,
so the output is embedded directly in README.md.

Usage: python tools/gen_neural_stl.py > assets/neural-net.stl
"""
import math

LAYERS = [3, 5, 5, 2]   # nodes per layer
LAYER_GAP = 14.0
NODE_GAP = 7.0
NODE_R = 1.6
EDGE_R = 0.22


def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def norm(a):
    n = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


tris = []


def tri(a, b, c):
    tris.append((a, b, c))


def octahedron(c, r):
    px, nx = add(c, (r, 0, 0)), add(c, (-r, 0, 0))
    py, ny = add(c, (0, r, 0)), add(c, (0, -r, 0))
    pz, nz = add(c, (0, 0, r)), add(c, (0, 0, -r))
    ring = [px, py, nx, ny]
    for i in range(4):
        a, b = ring[i], ring[(i + 1) % 4]
        tri(pz, a, b)
        tri(nz, b, a)


def prism(p, q, r):
    d = norm(sub(q, p))
    helper = (0, 0, 1) if abs(d[2]) < 0.9 else (1, 0, 0)
    u = norm(cross(d, helper))
    v = cross(d, u)
    offs = [add(mul(u, r * math.cos(t)), mul(v, r * math.sin(t)))
            for t in (0, 2 * math.pi / 3, 4 * math.pi / 3)]
    P = [add(p, o) for o in offs]
    Q = [add(q, o) for o in offs]
    for i in range(3):
        j = (i + 1) % 3
        tri(P[i], P[j], Q[j])
        tri(P[i], Q[j], Q[i])


def layer_positions(idx, count):
    x = (idx - (len(LAYERS) - 1) / 2) * LAYER_GAP
    pts = []
    for k in range(count):
        # spread nodes on a slight arc so the model reads well in 3D
        y = (k - (count - 1) / 2) * NODE_GAP
        z = -0.08 * y * y
        pts.append((x, y, z))
    return pts


layers = [layer_positions(i, n) for i, n in enumerate(LAYERS)]
for pts in layers:
    for p in pts:
        octahedron(p, NODE_R)
for a, b in zip(layers, layers[1:]):
    for p in a:
        for q in b:
            prism(p, q, EDGE_R)

out = ["solid neural_net"]
for a, b, c in tris:
    n = norm(cross(sub(b, a), sub(c, a)))
    out.append(f"facet normal {n[0]:.3f} {n[1]:.3f} {n[2]:.3f}")
    out.append("outer loop")
    for v in (a, b, c):
        out.append(f"vertex {v[0]:.2f} {v[1]:.2f} {v[2]:.2f}")
    out.append("endloop")
    out.append("endfacet")
out.append("endsolid neural_net")
print("\n".join(out))
