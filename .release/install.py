from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma, shutil, subprocess
root = Path.cwd()
raw = lzma.decompress(base64.b64decode((root/'.release/flow-signoff.b64').read_text(), validate=True))
assert hashlib.sha256(raw).hexdigest() == '8cbdc42940257afe2400e6487130b1324ebcdbfd0c09cb78f337aea44328388c'
data = json.loads(raw)
for name, expected in data['expected'].items():
    rel = PurePosixPath(name)
    assert not rel.is_absolute() and '..' not in rel.parts
    assert rel.parts[0] in {'quotation_engine', 'templates', '.agents'} or name in {'AGENTS.md', 'README.md'}
    target = root/name
    if expected is None:
        assert not target.exists(), name
    else:
        assert hashlib.sha256(target.read_bytes()).hexdigest() == expected, name
assert subprocess.check_output(['git','hash-object','LATEST.md'],text=True).strip() == data['latest']['before_git_blob']
archive = root/'.agents/handoffs/2026-09-22-before-philpost-flow-signoff.md'
assert not archive.exists()
patch = root/'.release/changes.patch'
patch.write_text(data['patch'])
subprocess.run(['git','apply','--check',str(patch)], check=True)
subprocess.run(['git','apply',str(patch)], check=True)
shutil.copy2(root/'LATEST.md', archive)
(root/'LATEST.md').write_text(data['latest']['content'])
print('Installed verified flow/sign-off delta. All original source hashes matched.')
