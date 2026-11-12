"""Replace old GitHub repo URLs with new AgentCart AI repo URL."""
import os, re

OLD = "github.com/Shubham-Code-Bases/AgentCart-AI-Autonomous-AI-Shopping-Assistant"
NEW = "github.com/Shubham-Code-Bases/AgentCart-AI-Autonomous-AI-Shopping-Assistant"

SKIP_DIRS = {'.git', '__pycache__', '.pytest_cache', 'node_modules'}
SKIP_EXTS = {'.pyc', '.pyo', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
             '.pdf', '.woff', '.woff2', '.ttf', '.eot', '.zip'}

root = r"C:\Users\dell.000\Downloads\paypilot-main"

replaced_files = []

for dirpath, dirnames, filenames in os.walk(root):
    # Prune skip dirs
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fname in filenames:
        ext = os.path.splitext(fname)[1].lower()
        if ext in SKIP_EXTS:
            continue
        fpath = os.path.join(dirpath, fname)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            continue
        if OLD in content:
            new_content = content.replace(OLD, NEW)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            count = content.count(OLD)
            replaced_files.append((fpath, count))

if replaced_files:
    print(f"Updated {len(replaced_files)} file(s):")
    for fp, n in replaced_files:
        print(f"  [{n}x] {fp}")
else:
    print("No files contained old repo URL.")
