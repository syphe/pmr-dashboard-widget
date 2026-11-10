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
from profile_evidence import evidence


def gallery(rows):
    """Show provenance, visual calibration and live validation independently."""
    cards=[];counts={}
    for id,status,_ in rows:
        info=evidence(id,status);validation=info['validationStatus']
        counts[validation]=counts.get(validation,0)+1
        findings=info['auditFindings']
        details='<details><summary>'+str(len(findings))+' audit findings</summary><ul>'+''.join('<li>'+html.escape(s)+'</li>' for s in findings)+'</ul></details>' if findings else ''
        stamp=(ROOT/'inspection/previews'/(id+'.png')).stat().st_mtime_ns
        cards.append('<article data-id="'+html.escape(id.lower(),quote=True)+'" data-validation="'+validation+'">'
            +'<h2>'+html.escape(id)+'</h2><div class="badges"><span>'+info['calibrationStatus']+'</span>'
            +'<span class="'+validation+'">'+validation+'</span></div>'
            +'<p class="provenance">Capture: '+info['captureMethod']+' · Scene audit: '+info['sceneAuditStatus']+'</p>'
            +details+'<img loading="lazy" alt="'+html.escape(id,quote=True)+' dashboard with sample telemetry" src="previews/'+id+'.png?v='+str(stamp)+'"></article>')
    summary=f'{len(rows)} profiles · {counts.get("runtime-audited",0)} live audits passed · {counts.get("runtime-audit-findings",0)} live audits with findings · {counts.get("pending-runtime-audit",0)} waiting for a live audit'
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PMR dashboard catalogue</title>'
        +'<style>body{background:#171b20;color:#eee;font:16px system-ui;margin:2rem}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,480px),1fr));gap:1rem}article{background:#252a30;padding:1rem;border-radius:8px}article[hidden]{display:none}img{width:100%;margin-top:1rem}h2{font-size:18px;overflow-wrap:anywhere}.badges{display:flex;flex-wrap:wrap;gap:.5rem}.badges span{background:#3b444f;border-radius:4px;padding:.25rem .5rem;font-size:13px}.badges .runtime-audited{background:#20593b}.badges .runtime-audit-findings{background:#793f27}.provenance,aside{color:#b8c4d1;font-size:14px}input,select{font:inherit;background:#252a30;color:#eee;border:1px solid #66717e;border-radius:4px;padding:.6rem;margin:.5rem .5rem 1rem 0}details{margin-top:1rem;color:#ffcb75}li{margin:.4rem 0}</style>'
        +'<h1>PMR dashboard catalogue</h1><p>'+summary+'</p>'
        +'<aside>Original game artwork, rendered with sample telemetry. Capture method describes where layout data came from; calibration describes visual adjustment. '
        +'Runtime validation requires the car’s actual Motec component and telemetry, separately from mounted scene checks. A live audit does not establish pixel accuracy or full-range warning behaviour. Analogue clusters are excluded.</aside>'
        +'<label>Find a car <input id="search" type="search" placeholder="Vehicle ID" autocomplete="off"></label>'
        +'<label>Live validation <select id="validation"><option value="">All profiles</option><option>pending-runtime-audit</option><option>runtime-audited</option><option>runtime-audit-findings</option></select></label>'
        +'<span id="visible"></span><main>'+''.join(cards)+'</main>'
        +'<script>const search=document.getElementById("search"),validation=document.getElementById("validation");function filter(){let visible=0;for(const card of document.querySelectorAll("article")){card.hidden=!card.dataset.id.includes(search.value.trim().toLowerCase())||(validation.value!==""&&card.dataset.validation!==validation.value);if(!card.hidden)visible++;}document.getElementById("visible").textContent=visible+" shown";}search.addEventListener("input",filter);validation.addEventListener("change",filter);filter();</script></html>')


def runtime():
    lua=LuaRuntime(unpack_returned_tuples=True)
    lua.globals().ROOT=str(ROOT).replace('\\','/')+'/'
    lua.execute('''
unpack=table.unpack
DashboardMod={root=ROOT}
function source(path)
 if path=='dataS/s4sGame/scripts/main.lua' then return end
 local f=assert(io.open(path));local s=f:read('*a');f:close();assert(load(s,'@'..path))()
end
source(ROOT..'script.lua')
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
 potentialLap=82.66,oil_pressure=400000,fuel_pressure=300000,tcs=6,abs=8,map=3,mix=2,
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
 for _,control in ipairs(profile.paletteControls or {}) do values['palette_'..control.id]=m.readNumber(actor,control) end
 m.drawDashboard({left=0,bottom=0,width=1,height=1},profile,values)
 m.release()
end
''')
    return lua


def refresh_gallery():
    """Refresh audit badges without redrawing the unchanged sample images."""
    engine=runtime()
    rows=[(p.id,p.layoutStatus,None) for _,p in engine.globals().DashboardMod.profiles.items()]
    for id,_,_ in rows:
        if not (ROOT/'inspection/previews'/(id+'.png')).exists():raise FileNotFoundError('Render previews first: '+id)
    (ROOT/'inspection/catalog.html').write_text(gallery(rows),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vehicle',help='Render only this exact vehicle ID')
    parser.add_argument('--gallery-only',action='store_true',help='Refresh audit labels using existing sample images')
    args=parser.parse_args()
    if args.gallery_only:
        refresh_gallery();print('Refreshed gallery audit labels');return
    lua=runtime(); images={}; rows=[]; out=ROOT/'inspection/previews';out.mkdir(parents=True,exist_ok=True)
    canvas=None;w=h=0
    def overlay(path,x,y,rw,rh,uv,color):
        if path not in images: images[path]=Image.open(path).convert('RGBA')
        im=images[path];u=[uv[i] for i in range(1,9)]
        im=im.crop((round(u[0]*im.width),round((1-u[3])*im.height),round(u[4]*im.width),round((1-u[1])*im.height)))
        if im.width<1 or im.height<1:return
        im=im.resize((max(1,round(rw*w)),max(1,round(rh*h))),Image.Resampling.LANCZOS)
        def tint(i):
            value=max(0,min(1,color[i+1]))
            if i<3 and path.endswith('palette.dds'):
                # Dynamic palette tint is linear in Overlay:setColor. The
                # white atlas lets this preview model the display encoding.
                value=12.92*value if value<=.0031308 else 1.055*value**(1/2.4)-.055
            return value
        im=Image.merge('RGBA',tuple(ch.point(lambda v:round(v*tint(i))) for i,ch in enumerate(im.split())))
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
    if not rows:raise SystemExit('Unsupported vehicle ID: '+str(args.vehicle))
    if not args.vehicle:
        font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
        for page in range(math.ceil(len(rows)/24)):
            sheet=Image.new('RGB',(1440,6*200),(26,29,32));draw=ImageDraw.Draw(sheet)
            for i,(id,status,im) in enumerate(rows[page*24:(page+1)*24]):
                x=i%4*360;y=i//4*200
                im.thumbnail((352,166));sheet.paste(im,(x+(360-im.width)//2,y+24))
                draw.text((x+5,y+5),id,font=font,fill='white')
            sheet.save(ROOT/f'inspection/catalog-{page+1}.jpg',quality=90)
        (ROOT/'inspection/catalog.html').write_text(gallery(rows),encoding='utf-8')
    print(f'Rendered {len(rows)} profiles into {out}')


if __name__=='__main__':main()
