"""Fail if private game assets/captures are still tracked in the Git index."""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def private_path(path):
    if path.startswith(('assets/','catalog/sources/','catalog/geometry/','reference/')):return True
    if path.startswith('inspection/'):
        return not path.endswith('.lua') or Path(path).name.startswith('.live-')
    return path in {'local_bootstrap.lua','catalog/files.json','catalog/vehicles.json','catalog/REPORT.md',
                    'tools/editor_geometry_jobs.lua'} or path.lower().endswith('.dds')


def main():
    result=subprocess.run(['git','-c','safe.directory='+ROOT.as_posix(),'ls-files','-z'],cwd=ROOT,
                          check=True,capture_output=True)
    blocked=[p for p in result.stdout.decode('utf-8').split('\0') if p and private_path(p)]
    if blocked:
        raise SystemExit('Private game-derived files are still tracked:\n'+'\n'.join(blocked))
    print('Git index contains no game textures, captured XML/geometry, previews, or local asset bundles')


if __name__=='__main__':main()
