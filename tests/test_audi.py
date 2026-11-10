"""Audi cockpit regressions: palette states, pre-lap delta and fitted text."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'.tools/python')]
from preview_catalog import runtime

engine=runtime()
engine.execute('''
local m=DashboardMod
local native=actor.getVehicleParamValue
actor.components={AIComp={xmlFilename='data/vehicles/Audi_R8_LMS_GT3_EVO/data/audi_actor.xml'}}
actor.getVehicleParamValue=function(self,param)
 if param:find('tyre_temp',1,true) then return true,39 end
 return native(self,param)
end
g_racingManager={playerVehicleData={vehicleActor=actor,bestValidLapTime={invalid=true,timeSeconds=0}}}
m.refresh(16)
assert(m.profile.id=='Audi_R8_LMS_GT3_EVO')
assert(m.values.lapDelta_digit==0,'Audi must show native zero delta before a best lap')
local delta
for _,f in ipairs(m.profile.fields) do if f.param=='lapDelta' then delta=f end end
assert(m.format(delta,m.values.lapDelta_digit)=='0.00')
local paletteCalls={};local fontCalls={};local currentBox
paintOverlay=function(path,x,y,w,h,uv,color)
 if path:find('palette.dds',1,true) then paletteCalls[#paletteCalls+1]={color[1],color[2],color[3]} end
 if currentBox and path:find('DDU9.dds',1,true) then
  local p=m.profile;local crop=p.assets.crop
  local left=x*p.width+crop.x;local right=(x+w)*p.width+crop.x
  local top=(1-y-h)*p.height-p.topPadding+crop.y;local bottom=top+h*p.height
  assert(left>=currentBox.x-.001 and right<=currentBox.x+currentBox.width+.001,'Text crossed its horizontal box border')
  assert(top>=currentBox.y-.001 and bottom<=currentBox.y+currentBox.height+.001,'Text crossed its vertical box border')
  fontCalls[#fontCalls+1]=true
 end
end
drawFilledRect=function() end
m.drawDashboard({left=0,bottom=0,width=1,height=1})
assert(#paletteCalls==#m.profile.paletteControls)
for i,control in ipairs(m.profile.paletteControls) do
 local c=paletteCalls[i]
 if control.id=='tyreLFT' then assert(c[1]==0 and c[2]==.05 and c[3]==1,'Cold tyre fill must use native linear blue') end
 if control.id=='tyreLFP' then assert(c[1]==0 and c[2]==.3 and c[3]==0,'Healthy pressure fill must use native linear green') end
 if control.id=='gearBox' then assert(c[1]==.03 and c[2]==.03 and c[3]==.03,'Gear fill must avoid double display encoding') end
end
for _,field in ipairs(m.profile.fields) do
 if field.textBounds then
  currentBox=field.textBounds
  m.drawText(m.profile,{left=0,bottom=0,width=1,height=1},field,'12345:59.99',{1,1,1,1})
 end
end
assert(#fontCalls>100,'The long-value fit checks did not render glyphs')
currentBox=nil
g_racingManager.playerVehicleData.bestValidLapTime={invalid=false,timeSeconds=82}
sample.lapDelta=-.27;m.refresh(16)
assert(m.values.lapDelta_digit==-.27 and m.format(delta,m.values.lapDelta_digit)=='-0.27')
sample.lapDelta=nil;m.refresh(16)
assert(m.values.lapDelta_digit==nil and m.format(delta,nil)=='--','Missing live delta must remain unavailable after a valid best lap')
sample.engine_temp=130
actor.getVehicleParamValue=function(self,param)
 if param:find('tyre_temp',1,true) then return true,110 end
 return native(self,param)
end
paletteCalls={};m.refresh(16);m.drawDashboard({left=0,bottom=0,width=1,height=1})
for i,control in ipairs(m.profile.paletteControls) do
 if control.id=='tyreLFT' or control.id=='engine_tempBox' then
  local c=paletteCalls[i];assert(c[1]==1 and c[2]==0 and c[3]==0,'Hot tyre/engine warning must be red')
 end
end
''')
print('Audi checks passed: cold/normal/hot palette, pre-lap delta, invalid telemetry and long values inside all 17 boxes')
