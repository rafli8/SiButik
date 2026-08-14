import os
import hashlib

ROOT = r'd:\Riset MBKM\model results'
SRC = os.path.join(ROOT, 'Batik_Re-Palette', 'showcase', 'images')
DST = os.path.join(ROOT, 'hf_space', 'showcase', 'images')


def h(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]


print(f"{'Name':<55} {'Local':<14} {'HF':<14} {'SizeL':>10} {'SizeH':>10}  Status")
print('-' * 120)
diffs = []
src_files = sorted(os.listdir(SRC))
for name in src_files:
    p1 = os.path.join(SRC, name)
    p2 = os.path.join(DST, name)
    if not os.path.isfile(p1):
        continue
    s1 = os.path.getsize(p1)
    if not os.path.exists(p2):
        diffs.append((name, 'MISSING'))
        print(f"{name:<55} {h(p1):<14} {'-':<14} {s1:>10} {'-':>10}  MISSING in HF")
        continue
    s2 = os.path.getsize(p2)
    h1 = h(p1)
    h2 = h(p2)
    status = 'SAME' if (h1 == h2 and s1 == s2) else 'DIFF'
    if status == 'DIFF':
        diffs.append((name, status))
    print(f"{name:<55} {h1:<14} {h2:<14} {s1:>10} {s2:>10}  {status}")

print()
print(f'Total files in source: {len(src_files)}')
print(f'Different files: {len(diffs)}')
for d in diffs:
    print(' -', d)