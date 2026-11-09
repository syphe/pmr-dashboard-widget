"""Compatibility aliases for the prepared Supra/Mustang profile previews."""
from pathlib import Path
import argparse
import shutil
import sys
from preview_catalog import main

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--profile',choices=['supra','mustang'],default='supra')
args=parser.parse_args()
vehicle='Toyota_Supra_GT4' if args.profile=='supra' else 'Ford_Mustang_V8Supercar_2024'
sys.argv=[sys.argv[0],'--vehicle',vehicle]
main()
shutil.copyfile(ROOT/'inspection/previews'/(vehicle+'.png'),ROOT/'inspection'/(args.profile+'-preview.png'))
