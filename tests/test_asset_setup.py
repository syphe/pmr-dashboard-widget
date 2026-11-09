"""Steam discovery and setup from an authored-files-only checkout."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'.tools/python'))
from game_install import find_game_install
from lupa import LuaRuntime

scratch=ROOT/'.tools';scratch.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='setup-test-',dir=scratch) as directory:
    temp=Path(directory)
    steam=temp/'Steam';library=temp/'Secondary library';game=library/'steamapps/common/Custom PMR folder'
    (game/'data/vehicles').mkdir(parents=True)
    (game/'data/shared/alphabet').mkdir(parents=True)
    (game/'data/shared/alphabet/fonts.xml').write_text('<fonts/>')
    (steam/'steamapps').mkdir(parents=True)
    escaped=str(library).replace('\\','\\\\')
    (steam/'steamapps/libraryfolders.vdf').write_text('"libraryfolders" { "1" { "path" "'+escaped+'" } }')
    (library/'steamapps/appmanifest_123.acf').write_text('"AppState" { "name" "Project Motor Racing" "installdir" "Custom PMR folder" }')
    assert find_game_install(env={},steam_roots=[steam])==game.resolve()
    assert find_game_install(env={'PMR_INSTALL_DIR':str(game)},steam_roots=[])==game.resolve()
    try:find_game_install(temp/'missing',env={},steam_roots=[steam])
    except FileNotFoundError:pass
    else:raise AssertionError('An invalid explicit path silently fell back to another installation')
print('Steam secondary-library discovery and explicit-path validation passed')

try:installed=find_game_install()
except FileNotFoundError:
    print('Clean-checkout build skipped: no local PMR installation')
    raise SystemExit(0)

with tempfile.TemporaryDirectory(prefix='clean checkout with spaces-',dir=scratch) as directory:
    checkout=Path(directory)
    for folder,pattern in [('tools','*.py'),('profiles','*.lua'),('catalog','*.lua'),('catalog','exclusions.json'),('catalog','calibrations.json')]:
        (checkout/folder).mkdir(parents=True,exist_ok=True)
        for file in (ROOT/folder).glob(pattern):shutil.copyfile(file,checkout/folder/file.name)
    for file in ['script.lua','dashboard_widget.lua','profile_registry.lua']:
        shutil.copyfile(ROOT/file,checkout/file)
    assert not (checkout/'assets').exists()
    assert not (checkout/'catalog/geometry').exists()
    assert not (checkout/'catalog/sources').exists()
    assert not (checkout/'catalog/vehicles.json').exists()
    env=dict(os.environ)
    env['PYTHONPATH']=str(ROOT/'.tools/python')+os.pathsep+env.get('PYTHONPATH','')
    subprocess.run([sys.executable,str(checkout/'tools/setup_assets.py'),'--game',str(installed),
                    '--vehicle','Ford_Mustang_GT3_2023','--vehicle','Ford_Mustang_V8Supercar_2024'],env=env,check=True)
    assert (checkout/'assets/vehicles/Ford_Mustang_GT3_2023/background.dds').is_file()
    assert not (checkout/'assets/Ford_Mustang_V8Supercar_2024').exists()
    assert not (checkout/'assets/library').exists()
    assert not (checkout/'catalog/sources').exists()
    assert not (checkout/'catalog/geometry').exists()
    lua=LuaRuntime();lua.globals().entry=str(checkout/'local_bootstrap.lua').replace('\\','/')
    lua.execute('''
unpack=table.unpack
function source(path)
 if path:sub(1,6)=='dataS/' then return end
 local file=assert(io.open(path));local code=file:read('*a');file:close();assert(load(code,path))()
end
source(entry)
assert(#DashboardMod.profiles==1)
assert(DashboardMod.profiles[1].id=='Ford_Mustang_GT3_2023')
assert(not DashboardMod.installedVehicleIds.Ford_Mustang_V8Supercar_2024)
''')
    print('Authored-files-only checkout built assets and loaded its generated entry point without game captures, geometry exports, or DLC textures')
    exports=ROOT/'inspection'
    if all((exports/name).is_file() for name in ('mustang-background.dds','mustang-mask.dds')):
        subprocess.run([sys.executable,str(checkout/'tools/setup_assets.py'),'--game',str(installed),
                        '--vehicle','Ford_Mustang_V8Supercar_2024','--dlc-export',str(exports)],env=env,check=True)
        assert (checkout/'assets/Ford_Mustang_V8Supercar_2024/icons.dds').is_file()
        assert (checkout/'assets/Toyota_Supra_GT4/font.dds').is_file()
        lua.execute('''
source(entry)
assert(#DashboardMod.profiles==2)
assert(DashboardMod.installedVehicleIds.Ford_Mustang_V8Supercar_2024)
assert(DashboardMod.installedVehicleIds.Toyota_Supra_GT4)
assert(not DashboardMod.installedVehicleIds.Ford_Mustang_GT3_2023)
''')
        print('Optional local DLC export setup and its shared-font dependency passed')
