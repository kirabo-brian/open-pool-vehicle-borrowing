"""Prints the real import edges between layers and fails on a wrong direction.

Run from the project root:  py -B evidence/check_layer_dependencies.py
"""
import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ALLOWED = {
    "domain": set(),
    "application": {"domain"},
    "infrastructure": {"domain", "application"},
    "interface": {"domain", "application", "infrastructure"},
}

edges, bad = set(), []
for layer, allowed in ALLOWED.items():
    for path in (ROOT / layer).glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and node.module:
                target = node.module.split(".")[0]
                if target in ALLOWED and target != layer:
                    edges.add((layer, target))
                    if target not in allowed:
                        bad.append(f"{path.name}: {layer} -> {target}")

for src, dst in sorted(edges):
    print(f"{src} -> {dst}")
if bad:
    print("WRONG DIRECTION:", *bad, sep="\n  ")
    sys.exit(1)
print("OK: all dependencies point inward")
