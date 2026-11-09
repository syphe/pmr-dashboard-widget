"""Bake palette fill widgets into bounded, cached overlay atlases."""
import math
from PIL import Image, ImageChops
from dds import save_dds


def fill_atlases(maps,widgets,out,width,height):
    masks=[Image.open(p).convert('RGB').resize((width,height)) for n,p in maps.items() if n in ('maskMap1','maskMap2')]
    gauges=[];assets={}
    for w in widgets:
        if w['type']!='palShaderslider' or not w.get('sParam') or not masks:continue
        key=tuple(map(int,w['sParam'].split('_')))
        intensity=Image.new('L',(width,height))
        for mask in masks:
            values=[]
            for rgb in mask.getdata():
                peak=max(rgb)
                values.append(peak if peak and tuple(round(c/peak*3) for c in rgb)==key else 0)
            layer=Image.new('L',(width,height));layer.putdata(values)
            intensity=ImageChops.lighter(intensity,layer)
        box=intensity.getbbox()
        if not box:continue
        ramp=intensity.crop(box);bw,bh=ramp.size
        # Downsample oversized authored masks for a bounded GPU allocation.
        scale=min(1,512/bw,256/bh);fw,fh=max(1,round(bw*scale)),max(1,round(bh*scale))
        ramp=ramp.resize((fw,fh),Image.Resampling.LANCZOS)
        cols,rows,count=9,8,65
        aw=2**math.ceil(math.log2(fw*cols));ah=2**math.ceil(math.log2(fh*rows))
        atlas=Image.new('RGBA',(aw,ah))
        for frame in range(count):
            cutoff=255*(1-frame/(count-1))
            alpha=ramp.point(lambda v:round(max(0,min(1,(v-cutoff)/4))*255) if v else 0)
            tile=Image.new('RGBA',(fw,fh),'white');tile.putalpha(alpha)
            atlas.paste(tile,(frame%cols*fw,frame//cols*fh))
        id=w['name'];file='gauge-'+id+'.dds';save_dds(atlas,out/file)
        assets[id]={'file':file,'x':box[0],'y':box[1],'width':fw,'height':fh,
            'displayWidth':bw,'displayHeight':bh,'frames':count,'columns':cols,'atlasWidth':aw,'atlasHeight':ah}
        gauge={'id':id,'param':w.get('vehicleParam'),'min':float(w.get('minValue',0)),
            'max':float(w.get('maxValue',1)),'color':[float(w.get(c,1)) for c in 'rgb']+[1]}
        for source,target in [('highThreshold','high'),('lowThreshold','low')]:
            if source in w:gauge[target]=float(w[source])
        gauges.append(gauge)
    return gauges,assets
