"""Render the actual Lua draw path through Pillow for visual layout checks."""
from pathlib import Path
import sys
import argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image, ImageDraw
from lupa import LuaRuntime

lua=LuaRuntime(unpack_returned_tuples=True)
parser=argparse.ArgumentParser()
parser.add_argument('--profile',choices=['supra','mustang'],default='supra')
args=parser.parse_args()
W,H=(1724,1022) if args.profile=='supra' else (2048,1104)
canvas=Image.new('RGBA',(W,H),(12,15,18,255))
images={}
def overlay(path,x,y,w,h,uv,color):
    if path not in images: images[path]=Image.open(path).convert('RGBA')
    im=images[path]
    u=[uv[i] for i in range(1,9)]
    im=im.crop((round(u[0]*im.width),round((1-u[3])*im.height),round(u[4]*im.width),round((1-u[1])*im.height)))
    if im.width<1 or im.height<1: return
    im=im.resize((max(1,round(w*W)),max(1,round(h*H))),Image.Resampling.LANCZOS)
    channels=im.split()
    im=Image.merge('RGBA',tuple(ch.point(lambda v:round(v*max(0,min(1,color[i+1])))) for i,ch in enumerate(channels)))
    canvas.alpha_composite(im,(round(x*W),round((1-y-h)*H)))
def rect(x,y,w,h,r,g,b,a):
    ImageDraw.Draw(canvas).rectangle((round(x*W),round((1-y-h)*H),round((x+w)*W),round((1-y)*H)),fill=tuple(round(c*255) for c in (r,g,b,a)))
lua.globals().paintOverlay=overlay
lua.globals().drawFilledRect=rect
lua.execute('''
unpack=table.unpack
DashboardMod={root=ROOT}
Overlay={}
function Overlay.new(filename,x,y,w,h)
 local o={filename=filename,uv={0,0,0,1,1,0,1,1},color={1,1,1,1}}
 function o:setPosition(x,y) self.x,self.y=x,y end
 function o:setDimension(w,h) self.w,self.h=w,h end
 function o:setUVs(uv) self.uv=uv end
 function o:setColor(...) self.color={...} end
 function o:render() paintOverlay(self.filename,self.x,self.y,self.w,self.h,self.uv,self.color) end
 function o:delete() end
 return o
end
'''.replace('root=ROOT','root='+repr(str(ROOT).replace('\\','/')+'/')))
for path in ['assets/supra/metadata.lua','assets/mustang/metadata.lua','profiles/supra.lua','profiles/mustang.lua','dashboard_widget.lua']:
    lua.execute((ROOT/path).read_text())
lua.execute('''
local m=DashboardMod
m.clock=0
local values={fuelPrevious=2.35,fuelUsed=1.76,brakeBias=59,best=82.93,actual=41.27,predicted=82.66,
 delta=-.27,gear=4,speed=186,fuel=53,oil=92,water=91,pressureFL=1.91,pressureFR=1.92,
 pressureRL=1.90,pressureRR=1.93,powerSteering=0,throttleLabel=0,tc=6,abs=8,
 gauge_rpm=6800,gauge_oil=92,gauge_water=91,gauge_fuel=53,shiftStart=5600,shiftEnd=7350}
values.engineTemp=109;values.position=17;values.lap=6;values.map=3;values.race=1
values.indicator_lights=1;values.indicator_wiper=0;values.indicator_frontLocked=0;values.indicator_rearLocked=0
PROFILE_INDEX=PROFILE_INDEX or 1
m.drawDashboard({left=0,bottom=0,width=1,height=1},m.profiles[PROFILE_INDEX],values)
'''.replace('PROFILE_INDEX=PROFILE_INDEX or 1','PROFILE_INDEX='+('1' if args.profile=='supra' else '2')))
output=ROOT/('inspection/'+args.profile+'-preview.png')
canvas.convert('RGB').save(output)
print(output)
