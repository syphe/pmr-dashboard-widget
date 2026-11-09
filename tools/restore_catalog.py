"""Restore the captured subset of installed game data for offline rebuilding.

This restores only archived dashboard dependencies, not a playable game install.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil

ROOT=Path(__file__).resolve().parents[1]


def restore(destination,link=False,verify_only=False):
    destination=destination.resolve()
    rows=json.loads((ROOT/'catalog/files.json').read_text())
    for row in rows:
        source=ROOT/row['file']
        if hashlib.sha256(source.read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('Archive hash mismatch: '+row['file'])
        target=(destination/row['source']).resolve()
        if not target.is_relative_to(destination):raise ValueError('Unsafe archive path: '+row['source'])
        if verify_only:continue
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest()!=row['sha256']:
                raise ValueError('Refusing to overwrite a different file: '+str(target))
            continue
        if link:os.link(source,target)
        else:shutil.copyfile(source,target)
    return len(rows)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',type=Path,default=ROOT/'inspection/restored-game')
    parser.add_argument('--link',action='store_true',help='Use local hard links; treat restored data as read only')
    parser.add_argument('--verify-only',action='store_true')
    args=parser.parse_args()
    print('Verified' if args.verify_only else 'Restored',restore(args.destination,args.link,args.verify_only),'archived files')
