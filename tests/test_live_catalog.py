"""Old logs and live capture helpers must exclude custom vehicles and liveries."""
from pathlib import Path
import json
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'.tools/python'))
import live_catalog
from lupa import LuaRuntime

definitions=[
    {'key':'base','definition':{'ID':'base','isMod':False,'vehicleRootPath':'data/vehicles/Base',
      'ActorFile':'data/vehicles/Base/data/actor.xml','VehicleClass':'GT',
      'Liveries':{'1':{'Name':'Original','rootPath':'data/vehicles/Base'},
                  '2':{'Name':'Custom paint','rootPath':'C:/PMR/mods/paint'}}}},
    {'key':'dlc','definition':{'ID':'dlc','isMod':False,'vehicleRootPath':'dlcS/pack/vehicles/DLC',
      'ActorFile':'dlcS/pack/vehicles/DLC/data/actor.xml','VehicleClass':'GT'}},
    {'key':'custom','definition':{'ID':'custom','isMod':True,'vehicleRootPath':'C:/PMR/mods/custom',
      'ActorFile':'C:/PMR/mods/custom/data/actor.xml','VehicleClass':'Custom'}},
    {'key':'unflagged','definition':{'ID':'unflagged','vehicleRootPath':'C:/PMR/mods/unflagged',
      'ActorFile':'C:/PMR/mods/unflagged/data/actor.xml','VehicleClass':'Custom'}},
]
scratch=ROOT/'.tools';scratch.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='catalog-filter-',dir=scratch) as directory:
    temp=Path(directory);live_catalog.CAPTURE=temp
    lines=['2026-11-10 08:00:00 VEHICLE_CAPTURE BEGIN']
    lines += ['VEHICLE_CAPTURE DEF '+json.dumps(r) for r in definitions]
    lines += ['VEHICLE_ASSET_READY 4']
    for row in definitions:
        d=row['definition'];id=d['vehicleRootPath'].split('/')[-1]
        lines.append('VEHICLE_ASSET '+json.dumps({'vehicle':id,'source':d['ActorFile']}))
        lines.append('VEHICLE_ASSET_CAR '+json.dumps({'id':id}))
    log=temp/'old.log';log.write_text('\n'.join(lines),encoding='utf-8')
    live_catalog.refresh(log)
    filtered=json.loads((temp/'definitions.json').read_text())
    assert {r['key'] for r in filtered}=={'base','dlc'}
    assert set(filtered[0]['definition']['Liveries'])=={'1'}
    assert {r['vehicle'] for r in json.loads((temp/'asset-manifest.json').read_text())}=={'Base','DLC'}
    assert {r['id'] for r in json.loads((temp/'car-assets.json').read_text())}=={'Base','DLC'}
    assert all('/mods/' not in p.read_text() for p in temp.glob('*.json'))

lua=LuaRuntime(unpack_returned_tuples=True)
lua.globals().defs=lua.table_from({r['key']:r['definition'] for r in definitions},recursive=True)
output=[];lua.globals().print=output.append
lua.execute('''
DashboardMod={root='unused/'}
function createFolder() end
g_VehicleCatalogueManager={defs=defs,vehicleClassDef={GT={text='GT'},Custom={text='Custom'}}}
''')
lua.execute((ROOT/'inspection/vehicle-catalog-capture.lua').read_text())
captured=[json.loads(line.split('VEHICLE_CAPTURE DEF ',1)[1]) for line in output if line.startswith('VEHICLE_CAPTURE DEF ')]
assert {r['key'] for r in captured}=={'base','dlc'}
assert not any('/mods/' in line for line in output)
classes=next(json.loads(line.split('VEHICLE_CAPTURE CLASSES ',1)[1]) for line in output if line.startswith('VEHICLE_CAPTURE CLASSES '))
assert set(classes)=={'GT'}
lua.execute((ROOT/'inspection/capture-vehicle-assets.lua').read_text())
assert {d.ID for _,d in lua.globals().VehicleAssetCapture.defs.items()}=={'base','dlc'}
print('Official catalogue filters passed for old logs, custom liveries and both live capture helpers')
