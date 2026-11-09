"""Build README.md: regenerate SVGs, then fill README.template.md from content.json.

Usage (from repo root):  python tools/build.py
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

subprocess.run([sys.executable, str(ROOT / "tools" / "gen_svgs.py")], check=True)

data = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))

cells = []
for p in data["projects"]:
    cells.append(f'<a href="{p["url"]}"><img src="./assets/cards/{p["slug"]}.svg" width="49%" alt="{p["name"]}: {p["desc"]}"/></a>')
rows = ["<p>\n  " + "\n  ".join(cells[i:i + 2]) + "\n</p>" for i in range(0, len(cells), 2)]

values = {"CARDS": "\n".join(rows)}

template = (ROOT / "README.template.md").read_text(encoding="utf-8")
missing = sorted(set(re.findall(r"\{\{(\w+)\}\}", template)) - set(values))
if missing:
    sys.exit(f"Unknown placeholders: {', '.join(missing)}")

readme = re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], template)
with open(ROOT / "README.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(readme)
print(f"README.md written ({len(readme):,} chars).")
