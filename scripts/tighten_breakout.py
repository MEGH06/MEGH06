"""Restyle github-breakout SVGs for the profile.

1. Empty days become blank boxes with a thin outline, so only green
   contributions are filled. Broken bricks turn blank too.
2. Shrink the empty gap between the bricks and the paddle.

The generator puts the paddle ~100px below the grid. This moves the paddle up
and compresses only the part of the ball's path that is below the bricks, so
brick hits stay exactly where they were and the ball still meets the paddle.
"""
import re
import sys

GRID_BOTTOM = 125   # ball cy at/above this is inside the brick area: left untouched
NEW_GAP = 45        # px between the bottom of the bricks and the paddle


def outline_empty(svg: str) -> str:
    empty = re.search(r"\.c0\{fill:(#[0-9A-Fa-f]{6})\}", svg).group(1)
    dark = int(empty[1:3], 16) < 0x80
    stroke = "#30363d" if dark else "#d0d7de"   # GitHub's own border colours
    svg = svg.replace(f".c0{{fill:{empty}}}", ".c0{fill:transparent}", 1)
    svg = svg.replace(empty, "transparent")      # bricks that get broken
    svg = svg.replace("</style>", f"use{{stroke:{stroke};stroke-width:1}}</style>", 1)
    return svg


def tighten(svg: str) -> str:
    paddle_y = int(re.search(r'<g transform="translate\(0,(\d+)\)">', svg).group(1))
    ball_low = paddle_y - 8          # ball centre when it touches the paddle
    new_paddle_y = 117 + NEW_GAP
    new_ball_low = new_paddle_y - 8
    if new_paddle_y >= paddle_y:
        return svg
    k = (new_ball_low - GRID_BOTTOM) / (ball_low - GRID_BOTTOM)

    def remap(y: float) -> float:
        return y if y <= GRID_BOTTOM else GRID_BOTTOM + (y - GRID_BOTTOM) * k

    def fix_cy(m):
        vals = ";".join(f"{remap(float(v)):.1f}".rstrip("0").rstrip(".") for v in m.group(1).split(";"))
        return f'attributeName="cy" values="{vals}"'

    svg = re.sub(r'attributeName="cy" values="([^"]+)"', fix_cy, svg)
    svg = svg.replace(f'translate(0,{paddle_y})', f'translate(0,{new_paddle_y})')

    shrink = paddle_y - new_paddle_y
    m = re.search(r'<svg width="(\d+)" height="(\d+)" viewBox="0 0 (\d+) (\d+)"', svg)
    w, h = m.group(1), int(m.group(2))
    svg = svg.replace(m.group(0), f'<svg width="{w}" height="{h - shrink}" viewBox="0 0 {w} {h - shrink}"', 1)
    return svg


if __name__ == "__main__":
    for path in sys.argv[1:]:
        with open(path) as f:
            out = tighten(outline_empty(f.read()))
        with open(path, "w") as f:
            f.write(out)
        print("restyled", path)
