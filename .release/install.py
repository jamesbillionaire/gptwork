from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma, re, shutil, subprocess
root = Path.cwd()
raw = lzma.decompress(base64.b64decode((root/'.release/flow-signoff.b64').read_text(), validate=True))
assert hashlib.sha256(raw).hexdigest() == '8cbdc42940257afe2400e6487130b1324ebcdbfd0c09cb78f337aea44328388c'
data = json.loads(raw)
# Preserve the newer, independently fetched Legal-paper guidance. The transport
# contains an older skill-file context; only its template identifier changes.
skill_name = '.agents/skills/lavi-quotation/SKILL.md'
skill = root/skill_name
assert subprocess.check_output(['git','hash-object',skill_name],text=True).strip() == '254b44899b06ed5e02a169689e071ca4b47e38b1'
skill_before = skill.read_text()
assert skill_before.count('LAVI-QUOTATION-2026.4') == 1
assert 'Legal paper: 8.5 x 14 inches (612 x 1008 pt)' in skill_before
assert skill_name in data['expected']
del data['expected'][skill_name]
pattern = r'(?ms)^--- a/\.agents/skills/lavi-quotation/SKILL\.md\n.*?(?=^--- |\Z)'
data['patch'], removed = re.subn(pattern, '', data['patch'])
assert removed == 1, 'Expected exactly one older skill-file patch'
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
skill.write_text(skill_before.replace('LAVI-QUOTATION-2026.4','LAVI-QUOTATION-2026.5'))
shutil.copy2(root/'LATEST.md', archive)
(root/'LATEST.md').write_text(data['latest']['content'])
print('Installed verified flow/sign-off delta. Preserved independently verified current Legal-paper skill guidance.')
