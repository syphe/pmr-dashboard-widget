"""Load a portable runtime-only checkout without setup, captures or a game install."""
from pathlib import Path
import os
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
sys.path.insert(0,str(ROOT/'tools'))
from lupa import LuaRuntime
from check_repo_assets import runtime_assets

scratch=ROOT/'.tools';scratch.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='portable bundle with spaces-',dir=scratch) as directory:
    checkout=Path(directory)
    files=['script.lua','dashboard_widget.lua','profile_registry.lua','catalog/vehicles.lua']
    files += [p.relative_to(ROOT).as_posix() for p in (ROOT/'profiles').glob('*.lua')]
    files += runtime_assets()
    for name in files:
        target=checkout/name;target.parent.mkdir(parents=True,exist_ok=True)
        # Read-only hard links avoid copying the large binary bundle for this check.
        os.link(ROOT/name,target)
    assert not (checkout/'tools').exists()
    assert not (checkout/'assets/installed.lua').exists()
    assert not (checkout/'local_bootstrap.lua').exists()
    assert not (checkout/'catalog/sources').exists()
    assert not (checkout/'assets/library').exists()
    expected=len(list((checkout/'profiles').glob('*.lua')))
    for mode in ('standard','pmr','loader'):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.globals().entry=(checkout/'script.lua').as_posix()
        lua.globals().expectedRoot=checkout.as_posix()+'/'
        lua.globals().expectedCount=expected
        lua.execute('''
unpack=table.unpack
function source(path)
 if path=='dataS/s4sGame/scripts/main.lua' then return end
 local f=assert(io.open(path));local s=f:read('*a');f:close();assert(load(s,'@'..path))()
end
-- A previous generated availability list must not suppress bundled profiles.
DashboardMod={installedVehicleIds={Toyota_Supra_GT4=true}}
''')
        if mode=='pmr':
            lua.execute('''
local info=debug.getinfo
debug.info=function(fn,option)
 assert(option=='s');return '='..info(fn,'S').source:gsub('^@','')
end
debug.getinfo=nil
''')
        elif mode=='loader':
            lua.execute('g_currentModDirectory=expectedRoot:sub(1,-2);debug=nil')
        lua.execute('''
source(entry)
local m=DashboardMod
assert(m.root==expectedRoot,'Startup root was not resolved correctly')
assert(#m.profiles==expectedCount)
assert(m.installedVehicleIds==nil and m.installedAssetSources==nil)
for _,profile in ipairs(m.profiles) do
 local assets=profile.assets or m.supraAssets
 assert(io.open(m.root..profile.assetDirectory..assets.background.file)):close()
end
function getName(root) return root end
for _,id in ipairs({'Ford_Mustang_V8Supercar_2024','Chevrolet_Camaro_V8Supercar_2024'}) do
 local actor={components={AIComp={xmlFilename='dlcs/s1_dlc3/vehicles/'..id..'/data/car_actor.xml'}}}
 assert(m.findProfile(actor).id==id,'Bundled DLC profile was unavailable')
end
source(entry)
assert(#m.profiles==expectedCount,'Startup reload duplicated profiles')
''')
        print(f'Portable bundle loaded {expected} profiles using {mode} path discovery, without setup or game files')
