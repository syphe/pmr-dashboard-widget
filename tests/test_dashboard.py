"""Behavior checks for the shared Lua renderer, units, lifecycle and visibility."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from lupa import LuaRuntime

lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
unpack=table.unpack
DashboardMod={root='unused/'}
g_screenAspectRatio=16/9
GuiElement={}
function GuiElement.new(target)
 local o={absPosition={0,0},size={1,1},elements={}}
 function o:setAnchor() end
 function o:setPivot() end
 function o:setAbsolutePosition(x,y) self.absPosition={x,y} end
 function o:setSize(w,h) self.size={w,h} end
 return o
end
function GuiElement.update() end
function GuiElement.draw() end
local function controller()
 local o={elements={},movableWidgets={}}
 function o:addElement(w) self.elements[#self.elements+1]=w end
 function o:isHudVisibleReasonSet(reason) return self.hidden==reason end
 return o
end
g_gui={guis={HudOverlay={target=controller()},MovableWidgetsPage={target=controller()}}}
MovableWidgetsPage={loadedPositions={},originalPositions={},applyWidgetPlacements=function() end}
PauseManager={paused=false,isPaused=function(self) return self.paused end}
HudOverlay={HideReasons={GAME=0,PAUSE=1,PRE_RACE=2,POST_RACE=4,DEBUG=7}}
function getName(root) return root end
stockUpdates=0
function update() stockUpdates=stockUpdates+1 end
function actor(name,params)
 local a={active=true,components={car={root=name}},params=params or {}}
 function a:getVehicleParamValue(p) return self.params[p]~=nil,self.params[p] end
 function a:getForwardSpeedKPH() return -20 end
 function a:getShiftLightsRange() return 8000,6000,7500 end
 return a
end
g_racingManager={active=true,playerVehicleData={vehicleActor=actor('Toyota_Supra_GT4_Evo.i3d',{
 gear=0,revs=3000,['wheel1.tyre_pressure']=137831.328,lapTime={timeSeconds=41.27,invalid=false},
 bestLap={timeSeconds=82.93,invalid=false},lapDelta=-.27}),
 bestValidLapTime={timeSeconds=82.93,invalid=false}}}
''')
for file in ['assets/supra/metadata.lua','assets/mustang/metadata.lua','profiles/supra.lua','profiles/mustang.lua','dashboard_widget.lua']:
    lua.execute((ROOT/file).read_text())
lua.execute('''
local m=DashboardMod
m.install()
local a=g_racingManager.playerVehicleData.vehicleActor
assert(m.profile.id=='supra')
assert(math.abs(m.values.pressureFL-1.37831328)<.000001)
assert(m.values.actual==41.27 and m.values.speed==20)
assert(m.format({kind='gear'},0)=='N')
assert(m.format({kind='gear'},-1)=='R')
assert(m.format({kind='time'},82.93)=='1:22.93')
assert(m.format({kind='time'},59.999)=='1:00.00')
assert(m.format({},0/0)=='--')
assert(m.readNumber(a,{param='lapTime'})==41.27)
a.params.lapTime.invalid=true
assert(m.readNumber(a,{param='lapTime'})==nil)
assert(m.readNumber(a,{param='lapTime',allowInvalid=true})==41.27)
a.params.lapTime.invalid=false
assert(m.readNumber(a,{constant=0})==0)
assert(m.readNumber(a,{param='missing'})==nil)
assert(m.readNumber(a,{param='revs',scale=.5,offset=7})==1507)
assert(m.readNumber(a,{param='revs',convert=function(v) return v+9 end})==3009)
assert(m.readNumber(a,{param='revs',convert=function() return math.huge end})==nil)
assert(m.shouldDraw())
PauseManager.paused=true;assert(not m.shouldDraw());PauseManager.paused=false
local hud=g_gui.guis.HudOverlay.target
for _,reason in pairs(HudOverlay.HideReasons) do hud.hidden=reason;assert(not m.shouldDraw()) end
hud.hidden=nil
g_racingManager.playerVehicleData.sessionFinished=true;assert(not m.shouldDraw())
g_racingManager.playerVehicleData.sessionFinished=false
assert(m.shouldDraw())
local editor=g_gui.guis.MovableWidgetsPage.target
local h,e=hud.hudDashboard,editor.hudDashboard
m.register();m.register()
assert(#hud.elements==1 and #editor.movableWidgets==1)
local realRefresh=m.refresh
local calls=0
m.refresh=function() calls=calls+1 end
h:update(10);e:update(10);assert(calls==1)
g_gui.currentGuiName='MovableWidgetsPage'
h:update(10);e:update(10);assert(calls==2)
g_gui.currentGuiName=nil;m.refresh=realRefresh
MovableWidgetsPage.loadedPositions.hudDashboard={.2,.3}
h:update(1)
assert(h.absPosition[1]==.2 and h.absPosition[2]==.3)
-- Replacing the actor must discard the old readings, including missing values.
g_racingManager.playerVehicleData.vehicleActor=actor('OtherCar')
m.refresh(0);assert(m.profile==nil and next(m.values)==nil)
g_racingManager.playerVehicleData.vehicleActor=actor('Toyota_Supra_GT4_Evo.i3d',{gear=4})
m.refresh(0);assert(m.profile.id=='supra' and m.values.gear==4 and m.values.pressureFL==nil)
-- Reinstall and module reload must not stack update wrappers or duplicate widgets.
m.install();update(1);assert(stockUpdates==1)
''')
lua.execute((ROOT/'dashboard_widget.lua').read_text())
lua.execute('''
DashboardMod.install();update(1)
assert(stockUpdates==2)
assert(#g_gui.guis.MovableWidgetsPage.target.movableWidgets==1)
print('Dashboard behavior checks passed')
''')
lua.execute('''
local m=DashboardMod
g_racingManager.playerVehicleData.vehicleActor=actor('Ford_Mustang_V8Supercar_2024.i3d',{
 gear=3,revs=6500,map=2,engine_temp=108,israce=true,lights=true,wiper=false,frontLocked=0,rearLocked=1})
m.refresh(0)
assert(m.profile.id=='mustang_v8_evo' and m.values.map==2 and m.values.engineTemp==108)
assert(m.values.race==1 and m.values.qualifying==nil)
assert(m.values.indicator_lights==1 and m.values.indicator_wiper==0 and m.values.indicator_rearLocked==1)
assert(m.values.pressureFL==nil and m.values.gauge_rpm==6500)
assert(m.format({kind='time',decimals=1},82.93)=='1:22.9')
assert(m.format({kind='time',decimals=1},59.96)=='1:00.0')
assert(m.format({text='RACE'},1)=='RACE' and m.format({text='RACE'},0)=='')
assert(m.format({text='RACE'},nil)=='')
renderedPaths={}
Overlay={}
function Overlay.new(filename)
 local o={filename=filename}
 function o:setPosition() end
 function o:setDimension() end
 function o:setUVs() end
 function o:setColor() end
 function o:render() renderedPaths[self.filename]=true end
 function o:delete() end
 return o
end
function drawFilledRect(x,y,w,h) assert(w>=0 and h>=0 and x==x and y==y) end
m.drawDashboard({left=.3,bottom=.02,width=.4,height=.38})
assert(renderedPaths['unused/assets/mustang/background.dds'])
assert(renderedPaths['unused/assets/mustang/icons.dds'])
assert(renderedPaths['unused/assets/supra/font.dds'])
assert(not renderedPaths['unused/assets/supra/background.dds'])
local count=0;for _ in pairs(m.resources) do count=count+1 end
assert(count==3)
print('Mustang profile, shared font and indicator checks passed')
''')
for file in ['profiles/supra.lua','profiles/mustang.lua']:
    lua.execute((ROOT/file).read_text())
lua.execute("assert(#DashboardMod.profiles==2, 'Profile reload removed or duplicated a car')")
