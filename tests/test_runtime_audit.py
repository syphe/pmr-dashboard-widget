"""Exercise recorder lifecycle and prevent stale/incomplete evidence passing."""
from pathlib import Path
import copy
import json
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'.tools/python')]
from preview_catalog import runtime
from runtime_audit import check_live
from profile_evidence import evidence

engine=runtime()
engine.execute('''
local profile
for _,p in ipairs(DashboardMod.profiles) do if p.id=='Audi_R8_LMS_GT3_EVO' then profile=p end end
local field
for _,f in ipairs(profile.fields) do if f.id=='fuel_pressure_digit' then field=f end end
local actor={getVehicleParamValue=function(self,param) return param=='fuel_pressure',327200 end}
local value=DashboardMod.readNumber(actor,field)
assert(math.abs(value-3.272)<1e-9,'Audi live pressure fixture must convert Pa to bar')
assert(DashboardMod.format(field,value)=='3.3','Audi pressure must match native one-decimal output')
''')
engine.execute('''
local originalSource=source
DashboardAuditJobs={{id='Test_One',catalogueId='ID_Test_One',actorFile='data/vehicles/Test_One/data/car_actor.xml',
 profileSha256='test-hash',widgets={},bindingNames={'numbersGear'},scenes={{file='data/vehicles/Test_One/display.i3d',names={'numbersGear'}}},
 profile={fields={{id='gear',param='gear',kind='gear'},{id='speed',method='getForwardSpeedKPH',absolute=true,scale=.5,offset=1}},gauges={},indicators={},auxiliaryFields={}}}}
function source(path) if not path:find('.live-audit-jobs.lua',1,true) then originalSource(path) end end
g_VehicleCatalogueManager={defs={one={ID='ID_Test_One',Active=true,ActorFile='data/vehicles/Test_One/data/car_actor.xml'}}}
local function actor()
 return {components={AIComp={xmlFilename='data/vehicles/Test_One/data/car_actor.xml'},motec={componentType='MotecComponent',
  masterPage={name='TopPage',widgets={gear_digit={type='digits',node=7,nodeName='numbersGear',vehicleParam='gear',fontName='DDU10',align=2,updateText='4'}}},
  pages={{name='Page1',widgets={}}},currentPage=1}},
  getVehicleParamValue=function(self,p) return p=='gear',p=='gear' and 4 or nil end,
  getForwardSpeedKPH=function() return -20 end}
end
makeAuditActor=actor
g_racingManager={playerVehicleData={vehicleActor=actor()}}
function createFolder() end
outputs={};handles={};deleted=0;loads=0
function createXMLFile(name,path) handles[#handles+1]={path=path};return #handles end
function setXMLString(handle,key,value) handles[handle].value=value end
function saveXMLFile(handle) outputs[handles[handle].path]=handles[handle].value end
function delete() deleted=deleted+1 end
function loadXMLFile() return 99 end
function saveXMLFileTo() end
function loadI3DFile(file,physics,onCreate) assert(physics==false and onCreate==false);loads=loads+1;return 7 end
function getName(node) return node==7 and 'numbersGear' or 'child' end
function getTranslation() return 0,0,0 end
function getScale() return 1,1,1 end
function localToWorld() return 1,2,3 end
function localDirectionToWorld(node,x,y,z) return x,y,z end
function getNumOfChildren() return 0 end
ClassIds={SHAPE=1}
function getHasClassId() return false end
stockAuditUpdates=0
function update() stockAuditUpdates=stockAuditUpdates+1 end
originalUpdate=update
''')
script=(ROOT/'inspection/runtime-dashboard-audit.lua').read_text(encoding='utf-8')
engine.execute(script)
captured={k:json.loads(v) for k,v in engine.globals().outputs.items()}
live=next(v for k,v in captured.items() if '/live/' in k)
assert live['complete'] and live['pages'][0]['widgets'][0]['node']['name']=='numbersGear'
assert live['readings']['field:gear']['formatted']=='4'
assert live['readings']['field:speed']['value']==11
engine.execute('''
local a=DashboardRuntimeAudit
local wrapper=update;a:start();assert(update==wrapper,'Repeated start wrapped twice')
update(1000);assert(stockAuditUpdates==1)
a:runScenes(1,1);assert(loads==1)
assert(deleted>=3,'Temporary resources were not released')
a:stop();assert(update==originalUpdate)
a:start();g_racingManager.playerVehicleData.vehicleActor=makeAuditActor();update(1000)
assert(a.lastVehicle=='Test_One','New actor was not captured')
''')
engine.execute(script)
engine.execute('''
update(1000);assert(stockAuditUpdates==3,'Reload nested update wrappers')
DashboardRuntimeAudit:stop();assert(update==originalUpdate)
''')

job={'id':'Test_One','widgets':[{'page':'TopPage','attributes':{'name':'gear_digit','type':'digits','bindingId':'numbersGear','vehicleParam':'gear','font':'DDU10'}}],
     'profile':{'fields':[{'id':'gear_digit','param':'gear','font':'DDU10','kind':'gear','align':'right'}]}}
record=copy.deepcopy(live);record['readings']['field:gear_digit']=record['readings'].pop('field:gear')
findings,notes=check_live(job,record);assert not findings,findings
bad=copy.deepcopy(record);bad['complete']=False
assert check_live(job,bad)[0]==['Live capture incomplete']
bad=copy.deepcopy(record);bad['pages'][0]['widgets'][0]['properties']['fontName']='Other'
assert any('font' in f for f in check_live(job,bad)[0])
bad=copy.deepcopy(record);bad['readings']['field:gear_digit']['getterAvailable']=False
assert any('getter' in f for f in check_live(job,bad)[0])
numeric_job=copy.deepcopy(job);numeric_job['profile']['fields'][0].pop('kind')
bad=copy.deepcopy(record);bad['readings']['field:gear_digit']['formatted']='400000'
assert any('conversion/units' in f for f in check_live(numeric_job,bad)[0]),'A unit mismatch passed the audit'
bad=copy.deepcopy(record);bad['pages'][0]['widgets'][0]['properties']['updateText']='4.0'
assert not check_live(numeric_job,bad)[0] and check_live(numeric_job,bad)[1],'Equivalent numeric formatting should be a note'
with tempfile.TemporaryDirectory(dir=ROOT/'.tools',prefix='audit-evidence-') as directory:
    temp=Path(directory);(temp/'profiles').mkdir();(temp/'catalog').mkdir()
    (temp/'profiles/Test_One.lua').write_text('new definition')
    (temp/'catalog/runtime-audit.json').write_text(json.dumps({'vehicles':{'Test_One':{'profileSha256':'stale','validationStatus':'runtime-audited','sceneAuditStatus':'passed'}}}))
    result=evidence('Test_One','geometry-unverified',temp)
    assert result['validationStatus']=='pending-runtime-audit' and not result['auditCurrent']
print('Runtime audit checks passed: conversions, snapshots, scene cleanup, reload/stop, actor changes and stale/incomplete evidence')
