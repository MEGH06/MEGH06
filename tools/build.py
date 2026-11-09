"""Build README.md from README.template.md + profile.json + assets/neural-net.stl.

Usage (from repo root):  python tools/build.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

values = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
values["STL"] = (ROOT / "assets" / "neural-net.stl").read_text(encoding="ascii").strip()

template = (ROOT / "README.template.md").read_text(encoding="utf-8")
missing = sorted(set(re.findall(r"\{\{(\w+)\}\}", template)) - set(values))
if missing:
    sys.exit(f"profile.json is missing keys: {', '.join(missing)}")

readme = re.sub(r"\{\{(\w+)\}\}", lambda m: str(values[m.group(1)]), template)
(ROOT / "README.md").write_text(readme, encoding="utf-8")

placeholders = [k for k, v in values.items() if "YOUR_" in str(v) or v in ("#", "you@example.com")]
print(f"README.md written ({len(readme):,} chars).")
if placeholders:
    print("Still placeholder:", ", ".join(placeholders))
