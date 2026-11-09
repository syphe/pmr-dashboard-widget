"""Run every profile through the actual Lua renderer, with sample telemetry."""
from pathlib import Path
import argparse
import html
import json
import math
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image, ImageDraw, ImageFont
from lupa import LuaRuntime


def runtime():
    if not (ROOT/'assets/installed.lua').exists():
        raise SystemExit('Run python tools/setup_assets.py before generating previews')
    lua=LuaRuntime(unpack_returned_tuples=True)
    lua.globals().ROOT=str(ROOT).replace('\\','/')+'/'
    lua.execute('''
unpack=table.unpack
DashboardMod={root=ROOT}
function source(path) local f=assert(io.open(path));local s=f:read('*a');f:close();assert(load(s,path))() end
source(ROOT..'profile_registry.lua')
source(ROOT..'catalog/vehicles.lua')
source(ROOT..'assets/installed.lua')
for _,file in ipairs(DashboardMod.installedAssetSources) do source(ROOT..file) end
for _,id in ipairs({'Toyota_Supra_GT4','Ford_Mustang_V8Supercar_2024','Chevrolet_Camaro_V8Supercar_2024'}) do
 if DashboardMod.installedVehicleIds[id] then source(ROOT..'profiles/'..id..'.lua') end
end
for _,entry in ipairs(DashboardMod.catalog) do
 if DashboardMod.installedVehicleIds[entry.id] then source(ROOT..entry.file) end
end
source(ROOT..'dashboard_widget.lua')
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
sample={gear=4,revs=6800,fuel=53,fuelDelta=1.76,previousFuelDelta=2.35,averageFuel=2.2,
 oil_temp=92,water_temp=91,engine_temp=109,brakebias=59,lap=6,pos=17,remainingLaps=4,
 lapDelta=-.27,bestLap=82.93,lastLap=83.2,lapTime=41.27,predictedLap=82.66,
 potentialLap=82.66,oil_pressure=4,fuel_pressure=3,tcs=6,abs=8,map=3,mix=2,
 hybrid_charge=75,hybridStrat=3,hybridMode=2,front_arb=4,rear_arb=3,lights=1,
 israce=1,isqualifying=0,ispractice=0}
actor={getForwardSpeedKPH=function() return 186 end,
 getVehicleParamValue=function(self,param)
  if string.find(param,'tyre_pressure',1,true) then return true,191000 end
  if string.find(param,'tyre_temp',1,true) then return true,82 end
  if string.find(param,'brake_temp',1,true) then return true,450 end
  return sample[param]~=nil,sample[param]
 end}
function preview(profile)
 local m=DashboardMod;local values={shiftStart=5600,shiftEnd=7350,shiftMax=8000}
 for _,field in ipairs(profile.fields) do values[field.id]=m.readNumber(actor,field) end
 for _,gauge in ipairs(profile.gauges) do values['gauge_'..gauge.id]=m.readNumber(actor,gauge) end
 values.gauge_rpm=6800
 for _,ind in ipairs(profile.indicators or {}) do values['indicator_'..ind.id]=m.readNumber(actor,ind) end
 m.drawDashboard({left=0,bottom=0,width=1,height=1},profile,values)
 m.release()
end
''')
    return lua


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vehicle',help='Render only this exact vehicle ID')
    args=parser.parse_args()
    lua=runtime(); images={}; rows=[]; out=ROOT/'inspection/previews';out.mkdir(parents=True,exist_ok=True)
    canvas=None;w=h=0
    def overlay(path,x,y,rw,rh,uv,color):
        if path not in images: images[path]=Image.open(path).convert('RGBA')
        im=images[path];u=[uv[i] for i in range(1,9)]
        im=im.crop((round(u[0]*im.width),round((1-u[3])*im.height),round(u[4]*im.width),round((1-u[1])*im.height)))
        if im.width<1 or im.height<1:return
        im=im.resize((max(1,round(rw*w)),max(1,round(rh*h))),Image.Resampling.LANCZOS)
        im=Image.merge('RGBA',tuple(ch.point(lambda v:round(v*max(0,min(1,color[i+1])))) for i,ch in enumerate(im.split())))
        canvas.alpha_composite(im,(round(x*w),round((1-y-rh)*h)))
    def rect(x,y,rw,rh,r,g,b,a):
        ImageDraw.Draw(canvas).rectangle((round(x*w),round((1-y-rh)*h),round((x+rw)*w),round((1-y)*h)),
            fill=tuple(round(max(0,min(1,c))*255) for c in (r,g,b,a)))
    lua.globals().paintOverlay=overlay;lua.globals().drawFilledRect=rect
    for _,p in lua.globals().DashboardMod.profiles.items():
        if args.vehicle and p.id!=args.vehicle:continue
        w=1024;h=round(w*p.height/p.width)
        canvas=Image.new('RGBA',(w,h),(12,15,18,255))
        lua.globals().preview(p)
        canvas.convert('RGB').save(out/(p.id+'.png'))
        rows.append((p.id,p.layoutStatus,canvas.convert('RGB').copy()))
        images.clear()
    if not rows:raise SystemExit('Vehicle has no prepared assets: '+str(args.vehicle)+'. Run tools/setup_assets.py (with --dlc-export for DLC V8 Supercars).')
    if not args.vehicle:
        font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
        for page in range(math.ceil(len(rows)/24)):
            sheet=Image.new('RGB',(1440,6*200),(26,29,32));draw=ImageDraw.Draw(sheet)
            for i,(id,status,im) in enumerate(rows[page*24:(page+1)*24]):
                x=i%4*360;y=i//4*200
                im.thumbnail((352,166));sheet.paste(im,(x+(360-im.width)//2,y+24))
                draw.text((x+5,y+5),id,font=font,fill='white')
            sheet.save(ROOT/f'inspection/catalog-{page+1}.jpg',quality=90)
        cards=''.join('<article><h2>'+html.escape(id)+'</h2><p>'+html.escape(status or '')+'</p><img loading="lazy" src="previews/'+id+'.png"></article>' for id,status,_ in rows)
        (ROOT/'inspection/catalog.html').write_text('<!doctype html><meta charset="utf-8"><title>PMR dashboard catalogue</title>'
            +'<style>body{background:#171b20;color:#eee;font:16px system-ui;margin:2rem}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:1rem}article{background:#252a30;padding:1rem}img{width:100%}h2{font-size:18px}p{color:#ffcb75}</style>'
            +'<h1>PMR dashboard catalogue</h1><p>Original game artwork only. Sample telemetry; imported projections still require visual calibration. Analogue and custom replacement layouts are excluded. Existing hand-tuned profiles are identified separately.</p><main>'+cards+'</main>',encoding='utf-8')
    print(f'Rendered {len(rows)} profiles into {out}')


if __name__=='__main__':main()
