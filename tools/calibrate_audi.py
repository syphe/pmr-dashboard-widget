"""Prepare the Audi R8 LMS GT3 Evo's original dynamic palette and box fitting."""
from pathlib import Path
import json
import math
import hashlib
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image,ImageChops,ImageOps
from build_active_profiles import CapturedImporter,STAGE
from dds import save_dds
from refine_catalog import refine

ID='Audi_R8_LMS_GT3_EVO'


def palette(row):
    importer=CapturedImporter(STAGE,ROOT)
    scene=importer.scene(STAGE/'data/vehicles'/ID/row['scenes'][0])
    node=scene['nodes'][row['pageDefaults']['paletteBindingId']][0][0]
    material=scene['materials'][node.get('materialIds').split()[0]]
    maps={c.get('name'):scene['files'][c.get('fileId')] for c in material if c.tag=='Custommap'}
    masks=[Image.open(maps[k]).convert('RGB') for k in ('maskMap1','maskMap2') if k in maps]
    size=masks[0].size
    widgets=[w for w in row['widgets'] if w['type']=='colorcontrol' and w.get('sParam') and not w.get('bindingId')]
    keys={tuple(map(int,w['sParam'].split('_'))) for w in widgets}
    channels={key:Image.new('L',size) for key in keys}
    for mask in masks:
        assert mask.size==size
        layer={key:bytearray(size[0]*size[1]) for key in keys};opacity=bytearray(size[0]*size[1])
        for index,rgb in enumerate(mask.get_flattened_data()):
            peak=max(rgb)
            if not peak:continue
            opacity[index]=peak
            channel=layer.get(tuple(round(c/peak*3) for c in rgb))
            if channel is not None:channel[index]=peak
        # Later shader mask layers also contain static labels and outlines.
        # They occlude lower palette fills even when their own colour is static.
        remaining=ImageOps.invert(Image.frombytes('L',size,bytes(opacity)))
        for key in keys:
            channels[key]=ImageChops.add(ImageChops.multiply(channels[key],remaining),Image.frombytes('L',size,bytes(layer[key])))
    tiles=[];controls=[];regions={};x=y=shelf=0;atlas_width=2048
    for w in widgets:
        image=channels[tuple(map(int,w['sParam'].split('_')))]
        box=image.getbbox()
        if not box:continue
        alpha=image.crop(box);width,height=alpha.size
        if x+width>atlas_width:x=0;y+=shelf;shelf=0
        tile=Image.new('RGBA',alpha.size,'white');tile.putalpha(alpha)
        tiles.append((tile,x,y));regions[w['name']]={'x':box[0],'y':box[1],'width':width,'height':height,'sourceX':x,'sourceY':y}
        x+=width+2;shelf=max(shelf,height+2)
        def color(suffix):
            values=[float(w.get(c+suffix,row['defaults'].get(c+suffix,w.get(c,row['defaults'].get(c,1))))) for c in 'rgb']
            # Overlay:setColor receives linear RGB. The game performs display
            # encoding; pre-encoding here brightens it twice (notably .03 grey).
            return [max(0,min(1,v)) for v in values]+[1]
        control={'id':w['name'],'param':w.get('vehicleParam'),'color':color(''),'highColor':color('h'),'lowColor':color('l')}
        for source,target in [('highThreshold','high'),('lowThreshold','low')]:
            if source in w:control[target]=float(w[source])
        if control['param'] in ('fuel_pressure','oil_pressure') or control['param'].endswith('tyre_pressure'):control['scale']=.00001
        controls.append(control)
    atlas_height=2**math.ceil(math.log2(y+shelf))
    atlas=Image.new('RGBA',(atlas_width,atlas_height))
    for tile,x,y in tiles:atlas.paste(tile,(x,y))
    save_dds(atlas,ROOT/'assets/vehicles'/ID/'palette.dds')
    return controls,{'file':'palette.dds','width':atlas_width,'height':atlas_height,'regions':regions}


def main():
    row=next(r for r in json.loads((ROOT/'catalog/vehicles.json').read_text()) if r['id']==ID)
    controls,atlas=palette(row)
    # Rectangles are measured against the original texture's frame/mask artwork.
    # The existing background is UV-cropped and pasted at (0,0); field coordinates
    # retain the original texture origin, hence the crop.x offset below.
    boxes={
      'laptime_digit':(22,261,451,385,95), 'speed_digit':(532,263,866,349,89),
      'lapDelta_digit':(945,262,1371,384,95),'gear_digit':(539,420,859,783,320),
      'fuel_digit':(249,860,529,985,77),'revs_digit':(568,859,927,983,107),
      'engine_temp_digit':(967,859,1148,985,77),'fuel_pressure_digit':(1185,859,1370,985,77),
      'brakebias_digit':(30,860,211,984,57),
      'tyreP_LF_digits':(27,425,258,584,77),'tyreP_LR_digits':(27,622,258,784,77),
      'tyreP_RF_digits':(1136,425,1370,584,77),'tyreP_RR_digits':(1136,622,1370,784,77),
      'tyreT_LF_digits':(294,554,471,654,77),'tyreT_LR_digits':(294,687,471,783,77),
      'tyreT_RF_digits':(927,554,1106,654,77),'tyreT_RR_digits':(927,687,1106,783,77)}
    fields={}
    baseline=json.loads((ROOT/'catalog/sources'/ID/'layout.json').read_text())
    offset=baseline['assets']['crop']['x']
    for field in baseline['fields']:
        name=field['id'];config={'align':'right','includeInPrimary':True}
        if name in boxes:
            left,top,right,bottom,height=boxes[name]
            config.update(x=right+offset,y=(top+bottom)/2,height=height,
                          textBounds={'x':left+offset,'y':top,'width':right-left,'height':bottom-top})
            if name=='gear_digit':config['boxAlign']='center'
        fields[name]=config
    fields['lapDelta_digit'].update(noBestLapValue=0,format='%.2f',deltaColor=False,lowColor=[0,1,0,1])
    path=ROOT/'catalog/calibrations.json';config=json.loads(path.read_text())
    config[ID]={'layoutStatus':'geometry-calibrated-unverified','fields':fields,'paletteControls':controls,'paletteAtlas':atlas}
    path.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    refine({ID})
    # Unique source filenames avoid PMR's cached source() chunks during tuning.
    # Reload only this profile and the renderer; saved HUD placement is retained.
    from runtime_audit import prepare
    prepare()
    loader=(ROOT/'inspection/runtime-audit/loader.txt').read_text().strip()
    profile_text=(ROOT/'profiles'/(ID+'.lua')).read_text()
    renderer_text=(ROOT/'dashboard_widget.lua').read_text()
    revision=hashlib.sha256((profile_text+renderer_text).encode()).hexdigest()[:12]
    copies=[]
    for label,text in [('profile',profile_text),('renderer',renderer_text)]:
        copy=ROOT/'inspection'/('.live-audi-'+label+'-'+revision+'.lua')
        copy.write_text(text,encoding='utf-8');copies.append(copy.as_posix())
    from vehicle_catalog import lua
    jobs=json.loads((ROOT/'inspection/runtime-audit/jobs.json').read_text())
    index=next(i for i,j in enumerate(jobs,1) if j['id']==ID)
    apply=ROOT/'inspection'/('.live-audi-apply-'+revision+'.lua')
    apply.write_text('if DashboardRuntimeAudit then DashboardRuntimeAudit:stop() end\n'
                    +'\n'.join('source('+lua(path)+')' for path in copies+[loader])
                    +f'\nDashboardRuntimeAudit:runScenes({index},{index})\n',encoding='utf-8')
    (ROOT/'inspection/runtime-audit/audi-reload.txt').write_text(apply.as_posix(),encoding='utf-8')
    print(f'Calibrated {ID}: {len(controls)} original-mask colour controls and {len(boxes)} fitted readouts')
    print('Live reload: source('+lua(apply.as_posix())+')')


if __name__=='__main__':main()
