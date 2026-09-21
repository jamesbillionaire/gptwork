"""One-time, checksum-verified installation of the locally reviewed template release.
Runs only on the release branch. Main is promoted separately after CI verification.
"""
from pathlib import Path, PurePosixPath
import base64
import hashlib
import json
import lzma
import shutil

root = Path.cwd()
parts = [root / '.release' / f'part-{i:02d}.b64' for i in range(1, 11)]
raw = lzma.decompress(base64.b64decode(''.join(p.read_text().strip() for p in parts), validate=True))
expected = 'd1557a7c4865bbec7ce936c611e5f2f693b3ecafb3bff6343c3233ffece2bf88'
assert hashlib.sha256(raw).hexdigest() == expected, 'Transport checksum mismatch'
data = json.loads(raw)
assert isinstance(data, dict) and len(data) == 37
allowed_files = {'AGENTS.md', 'LATEST.md', 'README.md', 'requirements.txt', '.gitignore'}
allowed_roots = {'quotation_engine', 'templates', '.agents'}
for name, content in data.items():
    path = PurePosixPath(name)
    assert not path.is_absolute() and '..' not in path.parts and '\\' not in name
    assert name in allowed_files or path.parts[0] in allowed_roots, name
    assert isinstance(content, str)
    assert (root / path).resolve().is_relative_to(root.resolve())
legacy = root / 'legacy'
legacy.mkdir(exist_ok=True)
engine_archive = legacy / 'quotation_engine-pre-cpsc'
assert not engine_archive.exists(), 'Refusing to replace an existing archive'
shutil.copytree(root / 'quotation_engine', engine_archive)
shutil.copy2(root / 'AGENTS.md', legacy / 'AGENTS-pre-cpsc-2026.md')
shutil.copy2(root / 'requirements.txt', legacy / 'requirements-pre-cpsc.txt')
handoff = root / '.agents/handoffs/2026-09-21-prior-sfdhmc-handoff.md'
assert not handoff.exists()
handoff.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(root / 'LATEST.md', handoff)
logos = {
    'templates/lavi/cpsc-2026/logo.png': 'templates/lavi/quotation-2026/LAVI_New_Logo_2026.png',
    'templates/lifes-awesome/cpsc-2026/logo.png': 'templates/lifes-awesome/quotation-2026/Lifes-Awesome-Logo.png',
}
shutil.rmtree(root / 'quotation_engine')
for name, content in data.items():
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8', newline='\n')
for target, source in logos.items():
    (root / target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / source, root / target)
print('Installed 37 verified source files and 2 original logos; historical engine and handoff archived.')
