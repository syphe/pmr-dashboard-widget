"""Check that runtime assets are tracked and local research outputs are excluded."""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def private_path(path):
    if path.startswith(('assets/library/','catalog/sources/','catalog/geometry/','reference/')):return True
    if path.startswith('inspection/'):
        return not path.endswith('.lua') or Path(path).name.startswith('.live-')
    return path in {'local_bootstrap.lua','assets/installed.lua','assets/setup-report.json',
                    'catalog/files.json','catalog/vehicles.json','catalog/REPORT.md',
                    'tools/editor_geometry_jobs.lua'} or (path.startswith('assets/') and path.endswith('/sources.txt'))


def runtime_assets(root=ROOT):
    return sorted(p.relative_to(root).as_posix() for p in (root/'assets').rglob('*')
                  if p.is_file() and not private_path(p.relative_to(root).as_posix()))


def main():
    result=subprocess.run(['git','-c','safe.directory='+ROOT.as_posix(),'ls-files','-z'],cwd=ROOT,
                          check=True,capture_output=True)
    tracked=set(filter(None,result.stdout.decode('utf-8').split('\0')))
    blocked=sorted(p for p in tracked if private_path(p))
    if blocked:raise SystemExit('Local research/setup outputs are tracked:\n'+'\n'.join(blocked))
    assets=runtime_assets()
    if not assets or 'assets/metadata.lua' not in assets:raise SystemExit('Bundled runtime assets are missing')
    missing=sorted(set(assets)-tracked)
    if missing:raise SystemExit('Runtime assets must be added to Git:\n'+'\n'.join(missing))
    print(f'Git tracks {len(assets)} bundled runtime files; local research/setup outputs are excluded')


if __name__=='__main__':main()
