# coding: utf-8
"""Observe only setup artifacts; never import or execute product modules."""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location('setup_helper', HERE / 'bootstrap.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
inode_owners = {}
cross_regular = []
external_links = []
rows = []
for item in helper.ITEMS:
    root = Path(item['tree'])
    session = root / 'build/review-session'
    before = json.loads((session/'metadata/setup-before.json').read_text())
    cmds = json.loads((session/'metadata/dependency-commands.json').read_text())
    electron = json.loads((session/'metadata/electron-command.json').read_text())
    assert len(cmds) == 2 and all(x['exitCode'] == 0 for x in cmds) and electron['exitCode'] == 0
    assert helper.git(root,'rev-parse','HEAD') == item['reviewHead']
    assert helper.git(root,'status','--porcelain') == 'M AGENTS.md'
    links = []
    files_by_root = {}
    for name in helper.GENERATED:
        top = root/name
        file_count = 0
        for folder, dirs, files in os.walk(top,followlinks=False):
            for name2 in dirs+files:
                path=Path(folder)/name2
                st=path.lstat()
                if stat.S_ISREG(st.st_mode):
                    file_count += 1
                    key=(st.st_dev,st.st_ino)
                    other=inode_owners.setdefault(key,str(root))
                    if other != str(root):
                        cross_regular.append({'path':str(path),'otherTree':other,'device':st.st_dev,'inode':st.st_ino})
                elif stat.S_ISLNK(st.st_mode):
                    target=path.resolve()
                    if not target.is_relative_to(root):
                        value={'path':str(path),'linkText':os.readlink(path),'resolved':str(target)}
                        links.append(value)
                        external_links.append(value)
        files_by_root[name]=file_count
    raw=[]
    for path in [session/'raw/setup-1.log',session/'raw/setup-2.log',session/'raw/setup-3-electron.log']:
        data=path.read_bytes()
        raw.append({'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'fullText':data.decode()})
    metadata=[]
    for path in sorted((root/'.venv/lib/python3.12/site-packages').glob('*.dist-info/METADATA')):
        lines=path.read_text().splitlines()
        metadata.append({k:next((x[len(k)+2:] for x in lines if x.startswith(k+': ')),None) for k in ['Name','Version']})
    electron_path=root/'node_modules/electron/dist/Electron.app/Contents/MacOS/Electron'
    assert electron_path.is_file()
    after=helper.counts(root)
    receipt=dict(item,at=helper.now(),beforeGenerated=before['beforeGenerated'],afterGenerated=after,
        growth={k:after[k]-before['beforeGenerated'][k] for k in after},
        metricMeaning='Logical generated-entry lstat inventory, not OS metadata-operation measurement. Snapshot precedes writing this receipt. OS/app operation totals UNKNOWN.',
        commands=cmds+[electron],raw=raw,installedPythonDistributions=metadata,
        externalSymlinks=links,observedRegularEntriesByRoot=files_by_root,
        electronInstalledPath=str(electron_path),electronLaunched=False,productExecuted=False,
        normalValidationExecuted=False,normalValidationReady='NOT CLAIMED; dependency setup only',
        skippedNpmLifecycle=['electron-winstaller','fsevents'],
        head=helper.git(root,'rev-parse','HEAD'),branch=helper.git(root,'branch','--show-current'),status=helper.git(root,'status','--porcelain'))
    helper.dump(session/'metadata/setup-after.json',receipt)
    helper.dump(HERE/(root.name+'-after.json'),receipt)
    rows.append({k:receipt[k] for k in ['module','role','tree','reviewHead','product','growth','normalValidationReady']})
assert not cross_regular
# Only shared base interpreter links are permitted to escape each physical tree.
assert all('/.venv/bin/python' in x['path'] and Path(x['resolved']).name.startswith('python') for x in external_links), external_links
helper.dump(HERE/'isolation-verification.json',{'at':helper.now(),'trees':rows,'generatedRoots':helper.GENERATED,
    'crossTreeRegularInodeCollisions':cross_regular,'externalSymlinks':external_links,
    'scanMeaning':'Every directory entry under own setup-generated roots lstat; no peer task/opinion/status discovery; no product imports/execution.',
    'systemBaseTools':'Shared read-only Node/npm/uv/Python installation; .venv base interpreter symlinks listed, package files independent.',
    'osActualMetadataOperations':None,'appRuntimeOperationCounts':None})
print(json.dumps({'trees':len(rows),'crossTreeRegularInodeCollisions':len(cross_regular),'externalBaseLinks':len(external_links),'productExecuted':False}))
