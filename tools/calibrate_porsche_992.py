"""Calibrate the Porsche 992 GT3 R using its original artwork and font shader."""
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image
from dds import save_dds
from refine_catalog import refine
from vehicle_catalog import lua
from dash_geometry import Surface,load_nodes,points

ID='Porsche_992_GT3R'


def lights():
    row=next(r for r in json.loads((ROOT/'catalog/vehicles.json').read_text()) if r['id']==ID)
    nodes=load_nodes(ROOT/'catalog/geometry'/f'{ID}__Porsche_992_GT3R_Display.i3d.xml')
    surface=Surface(nodes['POR_992_GT3R_DISPLAY1'])
    lamps=[];stages=[]
    colors={'greenT':[.1,1,.2,1],'amberT':[1,.65,.05,1],'redT':[1,.1,.1,1]}
    widgets=[w for w in row['widgets'] if w['type']=='shiftlights']
    for index,widget in enumerate(widgets,1):
        key=next(k for k in colors if k in widget)
        numerator,denominator=map(float,widget[key].split('/'))
        stages.append({'fraction':numerator/denominator,'color':colors[key],
                       'bindingId':widget['bindingId']})
        projected=[surface.project(p) for p in points(nodes[widget['bindingId']])]
        # Each source shape contains two separated round meshes. Retain their
        # horizontal centres; pack the physical strip into the widget header.
        for side in (0,1):
            cluster=[u*2048 for u,v in projected if (u>=.5)==bool(side)]
            assert len(cluster)>=3,(widget['name'],'Missing paired lamp')
            diameter=40
            lamps.append({'x':(min(cluster)+max(cluster))/2-10-diameter/2,
                          'y':8,'width':diameter,'height':diameter,
                          'bindingId':widget['bindingId'],'sourceStage':index})
    lamps.sort(key=lambda lamp:lamp['x'])
    assert [lamp['sourceStage'] for lamp in lamps]==list(range(1,9))+list(range(8,0,-1))
    return lamps,{'count':len(lamps),'shape':'circle','order':'outside-in',
                  'stages':stages,'flashAtMax':True,
                  'source':'Original paired RPM lamp meshes and actor thresholds; outside-in visually confirmed'}


def font():
    resources=ROOT/'inspection/live-catalog/resources/data'
    source=resources/'shared/alphabet/fontMP_alpha.dds'
    image=Image.open(source).convert('L')
    scale=4
    image=image.resize((image.width*scale,image.height*scale),Image.Resampling.BICUBIC)
    # alphabetShader.xml uses smoothstep(.48,.52, distance) in ALPHA_BLENDED.
    def coverage(value):
        t=max(0,min(1,(value/255-.48)/.04))
        return round(255*t*t*(3-2*t))
    image=image.point(coverage)
    definition=next(f for f in ET.parse(resources/'shared/alphabet/fonts.xml').getroot() if f.get('name')=='GENERIC')
    glyphs={};width,height=image.size
    for char in definition.findall('character'):
        index=int(char.get('uvIndex'));col,row=index%37,index//37
        left,right=round(col*width/37),round((col+1)*width/37)
        top,bottom=round(row*height/2),round((row+1)*height/2)
        box=image.crop((left,top,right,bottom)).getbbox()
        if box:glyphs[char.get('value')]={'x':left+box[0],'y':top,'width':box[2]-box[0],'height':bottom-top}
    glyphs[' ']={'x':width-1,'y':height-1,'width':scale,'height':height//2}
    rgba=Image.new('RGBA',image.size,'white');rgba.putalpha(image)
    relative=f'assets/vehicles/{ID}/font-generic-coverage.dds'
    save_dds(rgba,ROOT/relative)
    return {'file':relative,'width':width,'height':height,'glyphs':glyphs,
            'source':{'source':'data/shared/alphabet/fontMP_alpha.dds',
                      'sha256':hashlib.sha256(source.read_bytes()).hexdigest()},
            'processing':'Original distance atlas, 4x coverage using alphabetShader smoothstep(.48,.52)'}


def main():
    baseline=json.loads((ROOT/'catalog/sources'/ID/'layout.json').read_text())
    crop=baseline['assets']['crop']
    # Boxes measured in the already-cropped background DDS, in texture pixels.
    boxes={
      'gear_digit':(800,140,1230,502,260),
      'speed_digit':(802,26,1228,128,68),
      'lap_digit':(1420,36,1554,108,50),
      'pos_digit':(1874,36,2008,108,50),
      'laptime_digit':(1242,192,1794,330,68),
      'abs_digit':(148,146,216,208,39),
      'dim_digit':(148,244,216,308,39),
      'ath_digit':(148,340,216,404,39),
      'mul_digit':(148,436,216,500,39),
      'oilt_digit':(530,144,780,222,45),
      'oil_pressure_digit':(530,240,780,318,45),
      'watert_digit':(530,336,780,414,45),
      'waterp_digit':(530,432,780,500,45),
      'delta_digits':(1248,398,1506,500,45),
      'predictedLap_digit':(1530,398,1794,500,45),
      'brakebias_digit':(1584,594,1772,670,34),
      'tyreP_LF_digit':(824,584,1006,676,45),
      'tyreP_RF_digit':(1034,584,1216,676,45),
      'tyreP_LR_digit':(824,676,1006,748,45),
      'tyreP_RR_digit':(1034,676,1216,748,45)}
    fields={}
    for field in baseline['fields']:
        name=field['id'];config={'align':'right','includeInPrimary':True}
        if name in boxes:
            left,top,right,bottom,size=boxes[name]
            config.update(x=right+crop['x'],y=(top+bottom)/2+crop['y'],height=size,
                          textBounds={'x':left+crop['x'],'y':top+crop['y'],'width':right-left,'height':bottom-top})
            if name=='gear_digit':config['boxAlign']='center'
        if field.get('text'):config['align']='left'
        fields[name]=config
    fields['waterp_digit']['format']='%.1f'
    # This actor's oil-pressure getter is PSI (11.8894 -> native 0.8 bar).
    # Fuel and tyre pressure readings use different source units.
    fields['oil_pressure_digit']['scale']=0.0689475729
    fields['delta_digits'].update(noBestLapValue=0,format='%.2f',deltaColor=False)
    fields['predictedLap_digit'].update(noBestLapValue=0,positive=False)
    path=ROOT/'catalog/calibrations.json';config=json.loads(path.read_text())
    lamps,light_config=lights()
    config[ID]={'layoutStatus':'geometry-calibrated-unverified','fields':fields,'fonts':{'GENERIC':font()},
                'shiftLights':lamps,'shiftLightConfig':light_config,'topPadding':56}
    path.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    refine({ID})
    from runtime_audit import prepare
    prepare()
    loader=(ROOT/'inspection/runtime-audit/loader.txt').read_text().strip()
    chunks=[(ROOT/'profiles'/(ID+'.lua')).read_text(),(ROOT/'dashboard_widget.lua').read_text()]
    revision=hashlib.sha256(''.join(chunks).encode()).hexdigest()[:12]
    copies=[]
    for label,chunk in zip(('profile','renderer'),chunks):
        copy=ROOT/'inspection'/f'.live-porsche-992-{label}-{revision}.lua'
        copy.write_text(chunk,encoding='utf-8');copies.append(copy.as_posix())
    jobs=json.loads((ROOT/'inspection/runtime-audit/jobs.json').read_text())
    index=next(i for i,j in enumerate(jobs,1) if j['id']==ID)
    apply=ROOT/'inspection'/f'.live-porsche-992-apply-{revision}.lua'
    apply.write_text('if DashboardRuntimeAudit then DashboardRuntimeAudit:stop() end\n'
        +'\n'.join('source('+lua(p)+')' for p in copies+[loader])
        +f'\nDashboardRuntimeAudit:runScenes({index},{index})\n',encoding='utf-8')
    print('Live reload: source('+lua(apply.as_posix())+')')


if __name__=='__main__':main()
