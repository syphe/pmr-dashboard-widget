"""Exercise physical lamp count, paired progression, native circles and cleanup."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from preview_catalog import runtime

engine=runtime()
engine.execute('''
local m=DashboardMod;local p
for _,profile in ipairs(m.profiles) do if profile.id=='Porsche_992_GT3R' then p=profile end end
assert(p.shiftLightConfig.count==16 and #p.shiftLights==16)
assert(p.shiftLightConfig.order=='outside-in' and p.shiftLightConfig.shape=='circle')
assert(#p.shiftLightConfig.stages==8)
local native=Overlay.new;local created,deleted=0,0
Overlay.new=function(...)
 local o=native(...)
 o.setSliceId=function(self,id) self.slice=id end
 o.delete=function() deleted=deleted+1 end
 return o
end
g_overlayManager={getSliceInfoById=function(self,id)
 return {filename=id,sliceId=id}
end}
local calls={};local rectangles=0
paintOverlay=function(path,x,y,w,h,uv,color)
 if path:find('ui_elements.',1,true) then calls[#calls+1]={path=path,x=x,y=y,w=w,h=h} end
end
drawFilledRect=function() rectangles=rectangles+1 end
local values={shiftStart=1000,shiftEnd=8000,shiftMax=9000}
local function draw(rpm)
 calls={};values.gauge_rpm=rpm
 m.drawDashboard({left=0,bottom=0,width=.32,height=.32*(16/9)*p.height/p.width},p,values)
 assert(#calls==16,'Physical lamp count must be independent of the eight actor controls')
 local lit={}
 for i,c in ipairs(calls) do
  if c.path=='ui_elements.shiftLight' then lit[#lit+1]=i end
  assert(math.abs(c.h/c.w-16/9)<.00001,'Lamp must be circular in screen pixels')
 end
 return table.concat(lit,',')
end
assert(draw(999)=='')
assert(draw(1000)=='1,16','Outer pair must light first')
assert(draw(4000)=='1,2,3,4,13,14,15,16','Paired progression must move inward')
assert(draw(8000)=='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16')
m.clock=.2
assert(draw(9000)=='','All lit lamps blink at the maximum RPM')
m.clock=0
-- Configuration order is functional, rather than just a descriptive label.
p.shiftLightConfig.order='inside-out'
assert(draw(1000)=='8,9')
p.shiftLightConfig.order='right-to-left';p.shiftLightConfig.stages=nil
assert(draw(1000)=='16')
p.shiftLightConfig.order='left-to-right'
assert(draw(1000)=='1')
local before=deleted;m.release();assert(deleted>=before+2,'Both native circle overlays must be released')
g_overlayManager=nil;rectangles=0
m.drawDashboard({left=0,bottom=0,width=.32,height=.22},p,values)
assert(rectangles>16,'Offline/no-slice fallback must draw circle strips')
-- Legacy profiles retain their original rectangular lamps and thresholds.
local mustang
for _,profile in ipairs(m.profiles) do if profile.id=='Ford_Mustang_V8Supercar_2024' then mustang=profile end end
rectangles=0;calls={}
m.drawDashboard({left=0,bottom=0,width=.32,height=.22},mustang,values)
assert(#calls==0)
assert(rectangles>=#mustang.shiftLights)
''')
print('Shift-light checks passed: 16 circular lamps, eight paired stages, configurable direction, flashing, cleanup and legacy profiles')
