"""Compatibility entry point for the DLC V8 Supercar texture converter."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('prepare_v8_supercar.py')),run_name='__main__')
