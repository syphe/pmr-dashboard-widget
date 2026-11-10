"""Catalogue coverage, identity isolation, asset integrity and draw-path checks."""
from pathlib import Path
import json
import math
import struct
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from preview_catalog import runtime
from catalog_policy import exclusion_reason

lua=runtime();mod=lua.globals().DashboardMod
captured=ROOT/'catalog/vehicles.json'
rows=json.loads(captured.read_text()) if captured.exists() else []
if rows:assert all(not r['unresolvedBindings'] for r in rows)
source_by_id={r['id']:r for r in rows}
excluded=[{'id':id,'profile':'profiles/'+id+'.lua'} for id in json.loads((ROOT/'catalog/exclusions.json').read_text())]
profile_count=len(list((ROOT/'profiles').glob('*.lua')))
assert len(mod.profiles)==profile_count
from profile_coverage import audit
coverage=audit()
assert sum(r['active'] for r in coverage)==sum(r['active'] and r['status'] in {'profile','excluded-analogue'} for r in coverage)
by_id={p.id:p for _,p in mod.profiles.items()}
enabled=[{'id':id} for id in by_id]
assert {p.stem for p in (ROOT/'profiles').glob('*.lua')}==set(by_id)
lua.globals().expectedProfileCount=profile_count
for row in excluded:
    assert row['id'] not in by_id
    assert not (ROOT/row['profile']).exists()
    assert not (ROOT/'assets/vehicles'/row['id']).exists()
    assert not (ROOT/'inspection/previews'/(row['id']+'.png')).exists()
    assert not (ROOT/'catalog/sources'/row['id']/'layout.json').exists()

lua.globals().rootPath=str(ROOT).replace('\\','/')+'/'
lua.execute('''
function getName(root) return root end
local m=DashboardMod
for _,p in ipairs(m.profiles) do
 local a={components={car={root=p.rootNames[1]}}}
 assert(m.findProfile(a).id==p.id,'Root identity collision: '..p.id)
 a.components.AIComp={xmlFilename='data/vehicles/'..p.id..'/data/vehicle_actor.xml'}
 a.components.car.root='UnrelatedModel.i3d'
 assert(m.findProfile(a).id==p.id,'XML identity failed: '..p.id)
end
assert(m.findProfile({components={car={root='Ford_Mustang_GT3_2023_extra.i3d'}}})==nil)
local a={components={car={root='Ford_Mustang_V8Supercar_2024.i3d'},
 AIComp={xmlFilename='data/vehicles/Ford_Mustang_GT4_2024/data/car_actor.xml'}}}
assert(m.findProfile(a).id=='Ford_Mustang_GT4_2024','Exact actor ID must take precedence')
a.components.AIComp=nil
a.components.AudioComp={actorXmlFileName='dlcs/s1_dlc3/vehicles/Ford_Mustang_V8Supercar_2024/data/car_actor.xml'}
assert(m.findProfile(a).id=='Ford_Mustang_V8Supercar_2024')
''')

gauge_count=0
for row in enabled:
    p=by_id[row['id']]
    if row['id'] in source_by_id and row['id']!='Toyota_Supra_GT4':
        expected={w['name'] for w in source_by_id[row['id']]['widgets'] if w['type']=='digits'}
        actual={f.id for _,f in p.fields.items()}|{f.id for _,f in (p.auxiliaryFields or lua.table()).items()}
        assert expected==actual,(row['id'],expected-actual,actual-expected)
    assert p.width>0 and p.height>0
    for _,field in p.fields.items():
        assert all(math.isfinite(field[k]) for k in ('x','y','height')) and field.height>0
        font=((p.fonts[field.font] if p.fonts is not None else None) or mod.fonts[field.font]) if field.font else (p.assets or mod.supraAssets).font
        assert font is not None and font.glyphs['-'] is not None
        directory=p.fontDirectory if p.fontDirectory is not None else p.assetDirectory
        assert (ROOT/(directory+font.file)).exists()
    meta=p.assets or mod.supraAssets
    assert (ROOT/(p.assetDirectory+meta.background.file)).exists()
    for _,gauge in p.gauges.items():
        gauge_count+=1;asset=meta.gauges[gauge.id]
        assert not asset.file.startswith('needle-')
        assert gauge.max>gauge.min
        assert (ROOT/(p.assetDirectory+asset.file)).exists()
        assert asset.width*asset.columns<=asset.atlasWidth
        assert asset.height*math.ceil(asset.frames/asset.columns)<=asset.atlasHeight

lua.execute('''
paintOverlay=function(path,x,y,w,h,uv,color)
 assert(x==x and y==y and w>0 and h>0)
end
drawFilledRect=function(x,y,w,h) assert(x==x and y==y and w>=0 and h>=0) end
for _,p in ipairs(DashboardMod.profiles) do preview(p) end
local m=DashboardMod
g_racingManager={playerVehicleData={vehicleActor=actor,bestValidLapTime={invalid=true,timeSeconds=0}}}
actor.components={car={root='Ford_Mustang_GT3.i3d'}}
m.refresh(16)
assert(m.profile.id=='Ford_Mustang_GT3_2023')
for _,f in ipairs(m.profile.fields) do
 if f.param=='lapDelta' then assert(m.values[f.id]==nil) end
end
for _,entry in ipairs(m.catalog) do
 source(rootPath..entry.file)
end
assert(#m.profiles==expectedProfileCount,'Reload duplicated catalogue entries')
-- Old synthetic profiles must not survive a script reload or re-registration.
local stub={id='Porsche_Carrera_Cup_1990',layoutStatus='analogue-recreation-unverified'}
assert(m.registerProfile(stub)==false)
assert(#m.profiles==expectedProfileCount)
table.insert(m.profiles,stub)
table.insert(m.profiles,{id='supra'})
table.insert(m.profiles,{id='mustang_v8_evo'})
source(rootPath..'profile_registry.lua')
assert(#m.profiles==expectedProfileCount,'Legacy or synthetic profiles were not removed')
for id in pairs(m.excludedVehicles) do
 assert(m.findProfile({components={AIComp={xmlFilename='data/vehicles/'..id..'/data/car_actor.xml'},
  car={root='Toyota_Supra_GT4_Evo.i3d'}}})==nil,'Excluded actor fell back to another profile')
end
''')
print(f'Catalogue checks passed: {profile_count} asset-based profiles, {len(excluded)} exclusions, {gauge_count} animated gauges; all draw paths exercised')
