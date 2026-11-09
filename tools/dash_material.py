"""Offline base-colour evaluation of the installed str4_MotecShader masks."""
import xml.etree.ElementTree as ET
from PIL import Image


def compose(maps, material, defaults, widgets, shader):
    parameters={p.get('name'):p.get('defaultValue') for p in ET.parse(shader).getroot().findall('./Parameters/Parameter')}
    parameters.update({p.get('name'):p.get('value') for p in material.findall('CustomParameter')})
    def rgba(text,default=(0,0,0,1)):
        return tuple(map(float,text.split())) if text else default
    size=max((Image.open(p).size for p in maps.values()),key=lambda s:s[0]*s[1],default=(1024,512))
    use_texture=float(parameters.get('use_backgroundTex',0))==1
    if use_texture and 'backgroundMap' in maps:
        base=Image.open(maps['backgroundMap']).convert('RGBA').resize(size)
    else:
        color=[float(defaults.get('dashBackground'+c,parameters.get('backgroundColor','0 0 0 1').split()[i])) for i,c in enumerate('RGB')]
        base=Image.new('RGBA',size,tuple(round(min(1,max(0,c))*255) for c in color)+(255,))
    palette={k[10:]:rgba(v) for k,v in parameters.items() if k.startswith('BaseColor_')}
    sliders={w.get('sParam') for w in widgets if w.get('type')=='palShaderslider'}
    for w in widgets:
        key=w.get('sParam')
        if key and w.get('type')=='colorcontrol' and not w.get('bindingId'):
            palette[key]=tuple(float(w.get(c,defaults.get(c,1))) for c in 'rgb')+(1,)
    for name in ('maskMap1','maskMap2'):
        if name not in maps:continue
        mask=Image.open(maps[name]).convert('RGB').resize(size)
        result=[]
        for rgb,bg in zip(mask.getdata(),base.getdata()):
            peak=max(rgb)
            if peak<1:result.append(bg);continue
            key='_'.join(str(round(c/peak*3)) for c in rgb)
            # Dynamic fills are kept off here and emitted as separate atlases.
            if key in sliders:result.append(bg);continue
            color=palette.get(key,(1,1,1,1));a=peak/255
            result.append(tuple(round(b*(1-a)+min(1,max(0,c))*255*a) for b,c in zip(bg[:3],color[:3]))+(255,))
        base.putdata(result)
    if float(parameters.get('enable_foreground',0)) and 'foregroundMap' in maps:
        base.alpha_composite(Image.open(maps['foregroundMap']).convert('RGBA').resize(size))
    return base
