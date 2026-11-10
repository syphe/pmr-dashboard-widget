"""Porsche 992 live-audit regressions: shader coverage, units and cell fitting."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'.tools/python')]
from PIL import Image
from preview_catalog import runtime

engine=runtime()
engine.execute('''
local m=DashboardMod
actor.components={AIComp={xmlFilename='data/vehicles/Porsche_992_GT3R/data/car_actor.xml'}}
sample.gear=0;sample.oil_pressure=50;sample.lapDelta=nil;sample.predictedLap=nil
g_racingManager={playerVehicleData={vehicleActor=actor,bestValidLapTime={invalid=true,timeSeconds=0}}}
m.refresh(16)
local p=m.profile;assert(p.id=='Porsche_992_GT3R')
local fields={};for _,field in ipairs(p.fields) do fields[field.id]=field end
assert(m.format(fields.gear_digit,m.values.gear_digit)=='N')
assert(m.format(fields.oil_pressure_digit,m.values.oil_pressure_digit)=='3.4','PSI-to-bar conversion')
assert(m.format(fields.waterp_digit,m.values.waterp_digit)=='25.6','Literal precision')
assert(m.format(fields.delta_digits,m.values.delta_digits)=='0.00')
assert(m.format(fields.predictedLap_digit,m.values.predictedLap_digit)=='0:00.0')
local currentBox;local calls=0
paintOverlay=function(path,x,y,w,h,uv,color)
 if currentBox then
  assert(path:find('font-generic-coverage.dds',1,true),'Profile coverage atlas must override the raw distance atlas')
  local crop=p.assets.crop
  local left=x*p.width+crop.x;local right=(x+w)*p.width+crop.x
  local top=(1-y-h)*p.height-p.topPadding+crop.y;local bottom=top+h*p.height
  assert(left>=currentBox.x-.001 and right<=currentBox.x+currentBox.width+.001,'Horizontal text overflow')
  assert(top>=currentBox.y-.001 and bottom<=currentBox.y+currentBox.height+.001,'Vertical text overflow')
  calls=calls+1
 end
end
drawFilledRect=function() end
for _,field in ipairs(p.fields) do
 if field.textBounds then
  currentBox=field.textBounds
  m.drawText(p,{left=0,bottom=0,width=1,height=1},field,'12345:59.99',{1,1,1,1})
 end
end
assert(calls==220,'All 20 cell-fit paths must render')
currentBox=nil
g_racingManager.playerVehicleData.bestValidLapTime={invalid=false,timeSeconds=82}
sample.lapDelta=-.27;sample.predictedLap=81.73;m.refresh(16)
assert(m.format(fields.delta_digits,m.values.delta_digits)=='-0.27')
assert(m.format(fields.predictedLap_digit,m.values.predictedLap_digit)=='1:21.7')
''')

# The native shader thresholds a distance field at .5. Baking coverage must
# remove its broad grey halo while retaining an antialiased boundary.
profile=engine.globals().DashboardMod.profile
font=profile.fonts['GENERIC'];glyph=font.glyphs['N']
image=Image.open(ROOT/font.file).getchannel('A')
tile=image.crop((glyph.x,glyph.y,glyph.x+glyph.width,glyph.y+glyph.height))
hist=tile.histogram();visible=sum(hist[1:])
assert hist[255]/visible>.65,'Coverage atlas still contains a distance-field halo'
assert sum(hist[1:255])>0,'Coverage atlas lost edge antialiasing'
print('Porsche 992 checks passed: native font coverage, PSI conversion, pre-lap values and all 20 text boxes')
