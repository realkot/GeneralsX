#!/usr/bin/env python3
"""Stage pinned source/resources from realkot/GeneralsX without deleting existing work."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, tarfile, urllib.request, shlex

repo=Path(__file__).resolve().parents[3]
manifest=json.loads((repo/'Dependencies/android-mirrors.json').read_text())
parser=argparse.ArgumentParser();parser.add_argument('--archive',type=Path);parser.add_argument('--shell',action='store_true');args=parser.parse_args()
cache=repo/'build/owned-dependencies';cache.mkdir(parents=True,exist_ok=True)
archive=args.archive or cache/'android-sources-20261016.tar.gz'
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
if not archive.exists():
    part=archive.with_suffix('.part')
    with urllib.request.urlopen(manifest['url'],timeout=180) as src,part.open('wb') as dst:shutil.copyfileobj(src,dst)
    if digest(part)!=manifest['sha256']:raise SystemExit('Source mirror checksum mismatch')
    part.rename(archive)
if digest(archive)!=manifest['sha256']:raise SystemExit('Source mirror checksum mismatch')
dest=cache/manifest['sha256'][:16]
if not dest.exists():
    dest.mkdir()
    with tarfile.open(archive) as tar:
        for item in tar.getmembers():
            path=(dest/item.name).resolve()
            if not path.is_relative_to(dest.resolve()) or not (item.isfile() or item.isdir()):raise SystemExit('Unsafe source archive member')
        tar.extractall(dest,filter='data')
    (dest/'complete').write_text(manifest['sha256'])
if not (dest/'complete').is_file():raise SystemExit('Incomplete prior extraction; preserved for inspection')
# Existing DXVK checkout is retained, including its patches and Git history.
dxvk=repo/'references/fbraz3-dxvk'
if not (dxvk/'meson.build').is_file():
    if dxvk.exists() and any(dxvk.iterdir()):raise SystemExit('Nonempty DXVK directory preserved; inspect before staging')
    shutil.copytree(dest/'sources/DXVK',dxvk,dirs_exist_ok=True)
    subprocess.run(['git','init','--quiet',str(dxvk)],check=True)
# GeneralsX @bugfix Codex 17/10/2026 Preserve legacy CompLibHeader include paths
# with the flat LZHL mirror without changing compression sources or archive bytes.
lzhl_alias=dest/'sources/CompLibHeader'
lzhl_source=dest/'sources/LZHL'
if not lzhl_alias.exists():lzhl_alias.symlink_to(lzhl_source,target_is_directory=True)
if lzhl_alias.resolve()!=lzhl_source.resolve():raise SystemExit('Conflicting LZHL include alias preserved for inspection')
cmake=dest/'sources.cmake'
cmake.write_text('\n'.join('set(FETCHCONTENT_SOURCE_DIR_'+row['name']+' "'+(dest/row['sourcePath']).as_posix()+'" CACHE PATH "Owned mirror" FORCE)' for row in manifest['sources'] if row['name']!='DXVK')+'\n')
fetch=dest/'fetchcontent';fetch.mkdir(exist_ok=True)
for name,target in [('SDL3-src','SDL3'),('SDL3_image-src','SDL3_IMAGE'),('openal-soft-src','OPENAL_SOFT')]:
    link=fetch/name
    if not link.exists():link.symlink_to(dest/'sources'/target,target_is_directory=True)
env={'GX_OWNED_CMAKE_FILE':str(cmake),'GX_FETCHCONTENT_SRC':str(fetch),'VCPKG_DOWNLOADS':str(dest/'downloads')}
if args.shell:
    for key,value in env.items():print('export '+key+'='+shlex.quote(value))
else:print(json.dumps(env,indent=2))
