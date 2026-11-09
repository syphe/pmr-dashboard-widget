"""Locate a loose-file PMR installation, including secondary Steam libraries."""
from pathlib import Path
import os
import re


def valid_install(path):
    path=Path(path)
    return (path/'data/vehicles').is_dir() and (path/'data/shared/alphabet/fonts.xml').is_file()


def steam_libraries(steam_root):
    root=Path(steam_root)
    yield root
    config=root/'steamapps/libraryfolders.vdf'
    if config.is_file():
        text=config.read_text(encoding='utf-8-sig',errors='replace')
        # Both current "path" records and old numeric library records.
        for value in re.findall(r'"(?:path|\d+)"\s*"([^"\r\n]+)"',text):
            if '/' in value or '\\' in value:
                yield Path(value.replace('\\\\','\\'))


def find_game_install(explicit=None,env=None,steam_roots=None):
    env=os.environ if env is None else env
    requested=explicit or env.get('PMR_INSTALL_DIR')
    if requested:
        path=Path(requested).expanduser().resolve()
        if not valid_install(path):
            raise FileNotFoundError(f'Not a PMR loose-file installation: {path} (expected data/vehicles and data/shared/alphabet/fonts.xml)')
        return path
    roots=list(steam_roots or [])
    if steam_roots is None:
        if os.name=='nt':
            import winreg
            for hive,key,value in [(winreg.HKEY_CURRENT_USER,r'Software\Valve\Steam','SteamPath'),
                                   (winreg.HKEY_LOCAL_MACHINE,r'SOFTWARE\WOW6432Node\Valve\Steam','InstallPath')]:
                try:
                    with winreg.OpenKey(hive,key) as handle:roots.append(Path(winreg.QueryValueEx(handle,value)[0]))
                except OSError:pass
        for variable,default in [('ProgramFiles(x86)',r'C:\Program Files (x86)'),('ProgramFiles',r'C:\Program Files')]:
            roots.append(Path(env.get(variable,default))/'Steam')
    seen=set()
    for steam in roots:
        for library in steam_libraries(steam):
            key=str(library.resolve()).lower()
            if key in seen:continue
            seen.add(key)
            direct=library/'steamapps/common/Project Motor Racing'
            if valid_install(direct):return direct.resolve()
            for manifest in (library/'steamapps').glob('appmanifest_*.acf'):
                text=manifest.read_text(encoding='utf-8-sig',errors='replace')
                name=re.search(r'"name"\s*"([^"]+)"',text)
                folder=re.search(r'"installdir"\s*"([^"]+)"',text)
                if name and folder and name[1].casefold()=='project motor racing':
                    candidate=library/'steamapps/common'/folder[1]
                    if valid_install(candidate):return candidate.resolve()
    raise FileNotFoundError('PMR installation not found. Pass --game "D:/SteamLibrary/steamapps/common/Project Motor Racing" or set PMR_INSTALL_DIR.')
