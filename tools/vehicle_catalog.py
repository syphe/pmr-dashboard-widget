"""Offline Motec import. No game process, debugger, or mounted DLC is used.

The manifest is lossless for the Motec XML; generated layouts are explicitly
drafts until their scene-to-texture calibration has been checked. Mesh files are
preserved because their vertex positions/UVs are not present in the scene XML.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tools/python'))
from PIL import Image, ImageDraw
from dash_geometry import load_nodes, layout
from dash_material import compose
from dash_gauges import fill_atlases
from dds import save_dds
from catalog_policy import exclusion_reason

DEFAULT_GAME = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Project Motor Racing')


def lua(value):
    if value is None: return 'nil'
    if isinstance(value, bool): return 'true' if value else 'false'
    if isinstance(value, str):
        return '"' + value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r') + '"'
    if isinstance(value, (int, float)): return str(round(value, 6))
    if isinstance(value, list): return '{' + ','.join(lua(v) for v in value) + '}'
    return '{' + ','.join('['+lua(k)+']='+lua(value[k]) for k in sorted(value)) + '}'


def vec(text, default=(0, 0, 0)):
    return tuple(map(float, text.split())) if text else default


def identity():
    return [[float(i == j) for j in range(4)] for i in range(4)]


def mul(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def transform(node):
    t=vec(node.get('translation')); s=vec(node.get('scale'), (1,1,1))
    x,y,z=(math.radians(v) for v in vec(node.get('rotation')))
    cx,sx,cy,sy,cz,sz=math.cos(x),math.sin(x),math.cos(y),math.sin(y),math.cos(z),math.sin(z)
    rx=[[1,0,0,0],[0,cx,-sx,0],[0,sx,cx,0],[0,0,0,1]]
    ry=[[cy,0,sy,0],[0,1,0,0],[-sy,0,cy,0],[0,0,0,1]]
    rz=[[cz,-sz,0,0],[sz,cz,0,0],[0,0,1,0],[0,0,0,1]]
    m=mul(mul(rz,ry),rx)
    for i in range(3):
        for j in range(3): m[i][j]*=s[j]
        m[i][3]=t[i]
    return m


class Importer:
    def __init__(self, game, output, copy_meshes=True):
        self.game=game.resolve(); self.data=self.game/'data'; self.output=output.resolve()
        self.copy_meshes=copy_meshes; self.blobs={}; self.fonts={}
        self.library=output/'assets/library'; self.library.mkdir(parents=True, exist_ok=True)
        self.calibrations=json.loads((ROOT/'catalog/calibrations.json').read_text()) if (ROOT/'catalog/calibrations.json').exists() else {}

    def resolve(self, ref, base):
        ref=ref.replace('\\','/')
        p=self.data/ref[6:] if ref.lower().startswith('$data/') else base/ref
        if p.exists(): return p
        if p.suffix.lower() in ('.png','.tga','.jpg') and p.with_suffix('.dds').exists(): return p.with_suffix('.dds')
        return None

    def blob(self, path):
        path=path.resolve()
        if path in self.blobs: return self.blobs[path]
        content=path.read_bytes(); digest=hashlib.sha256(content).hexdigest()
        relative='assets/library/'+digest[:24]+path.suffix.lower()
        dest=self.output/relative
        if not dest.exists(): dest.write_bytes(content)
        result={'source':str(path.relative_to(self.game)).replace('\\','/'), 'file':relative,
                'sha256':digest, 'bytes':len(content)}
        self.blobs[path]=result
        return result

    def scene(self, file):
        xml=ET.parse(file).getroot()
        files={f.get('fileId'):self.resolve(f.get('filename'),file.parent) for f in xml.findall('./Files/File')}
        materials={m.get('materialId'):m for m in xml.findall('./Materials/Material')}
        nodes={}
        def walk(node, matrix):
            matrix=mul(matrix,transform(node))
            nodes.setdefault(node.get('name'),[]).append((node,matrix))
            for c in node: walk(c,matrix)
        scene=xml.find('Scene')
        if scene is not None:
            for n in scene: walk(n,identity())
        return dict(path=file, xml=xml, files=files, materials=materials, nodes=nodes)

    def font(self, name):
        if name in self.fonts: return self.fonts[name]
        fonts=ET.parse(self.data/'shared/alphabet/fonts.xml').getroot()
        definition=next((f for f in fonts if f.get('name')==name),None)
        if definition is None: return self.font('GENERIC')
        self.blob(self.data/'shared/alphabet/fonts.xml')
        self.blob(self.data/'shared/alphabet/fontMaterialHolder.i3d')
        self.blob(self.data/'shaders/alphabetShader.xml')
        holder=self.scene(self.data/'shared/alphabet/fontMaterialHolder.i3d')
        node=holder['xml'].find('Scene')
        for ix in definition.get('node').split('|'): node=list(node)[int(ix)]
        mat=holder['materials'][node.get('materialIds')]
        tex=next(c for c in mat if c.tag=='Custommap' and c.get('name')=='alphaMap')
        source=holder['files'][tex.get('fileId')]; original=self.blob(source)
        im=Image.open(source).convert('L'); w,h=im.size
        degree=next((c for c in definition.findall('character') if c.get('value')=='!'),None)
        if degree is not None:
            index=int(degree.get('uvIndex'));cx=round((index%37+.25)*w/37);cy=round((index//37+.13)*h/2)
            cell=im.crop((round(index%37*w/37),round(index//37*h/2),round((index%37+1)*w/37),round((index//37+1)*h/2)))
            if not cell.getbbox():ImageDraw.Draw(im).ellipse((cx,cy,cx+max(4,w//185),cy+max(4,w//185)),fill=0,outline=255,width=2)
        glyphs={}
        # Glyph bounds within each atlas cell; retain complete row for baselines.
        for char in definition.findall('character'):
            index=int(char.get('uvIndex')); col,row=index%37,index//37
            x0,x1=round(col*w/37),round((col+1)*w/37); y0,y1=round(row*h/2),round((row+1)*h/2)
            box=im.crop((x0,y0,x1,y1)).getbbox()
            if box:
                glyphs[char.get('value')]={'x':x0+box[0],'y':y0,'width':box[2]-box[0],'height':y1-y0}
        # Some shipped fonts leave spaces/special characters blank.
        glyphs.setdefault('-',{'x':0,'y':0,'width':max(1,w//74),'height':h//2})
        glyphs[' ']={'x':w-1,'y':h-1,'width':1,'height':h//2}
        rgba=Image.new('RGBA',im.size,'white'); rgba.putalpha(im)
        rel='assets/fonts/'+name+'.dds'; dest=self.output/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        save_dds(rgba,dest)
        self.fonts[name]={'file':rel,'width':w,'height':h,'glyphs':glyphs,'source':original}
        return self.fonts[name]

    def bindings(self, widget):
        p=widget.get('vehicleParam'); f={'param':p} if p else {}
        if widget.get('setLabel') is not None:
            label=widget.get('setLabel')
            try: f={'constant':float(label)}
            except ValueError: f={'constant':1,'text':label}
        elif p=='speed':
            f={'method':'getForwardSpeedKPH','absolute':True}
            if widget.get('unitOverride')=='mph': f['scale']=1/1.609344
        elif p and p.endswith('tyre_pressure'): f['scale']=.00001
        if p=='gear': f['kind']='gear'
        if widget.get('zeroNeutral')=='true':f['zeroNeutral']=True
        fmt=widget.get('format','')
        if 'm:s' in fmt or (p in ('lapTime','bestLap','lastLap','predictedLap','potentialLap') and not fmt):
            f.update(kind='time',decimals=1 if fmt.endswith('.t') else 2,allowInvalid=p=='lapTime',positive=p!='lapTime')
        else:
            decimals=2 if 'f2' in fmt or '.h' in fmt else 1 if 'f1' in fmt or '.t' in fmt else 0
            if not fmt:
                if p and (p.endswith('tyre_pressure') or p in ('lapDelta','fuelDelta','previousFuelDelta','averageFuel')):decimals=2
                elif p in ('brakebias','oil_pressure','fuel_pressure'):decimals=1
            suffix='!C' if '!C' in fmt else 'L' if fmt.endswith('L') else ''
            f['format']='%'+('+' if fmt.startswith('+') else '')+'.'+str(decimals)+'f'+suffix
        if p=='lapDelta': f['deltaColor']=True
        for src,dst in [('highThreshold','high'),('lowThreshold','low')]:
            if src in widget: f[dst]=float(widget[src])
        f['boolean']=True  # Convert bool accessors; numeric readings are unchanged.
        return f

    def import_car(self, actor_file):
        actor_file=actor_file.resolve()
        vehicle=actor_file.relative_to(self.data/'vehicles').parts[0]
        out=self.output/'catalog/sources'/vehicle; out.mkdir(parents=True,exist_ok=True)
        actor=ET.parse(actor_file).getroot()
        self.blob(actor_file)
        motec=next(c for c in actor.findall('./components/component') if c.get('type')=='MotecComponent')
        defaults=dict(motec.find('default').attrib)
        pages=motec.find('pages'); selected=list(pages.findall('topPage'))+list(pages.findall('page'))[:1]
        widgets=[dict(w.attrib) for p in selected for w in p.findall('.//widget')]
        visibility={w.get('bindingId'):w.get('vehicleParam') for w in widgets if w['type']=='stateindicator'}
        main=next(iter(pages.findall('page')),None)
        pd=main.find('pagedefault') if main is not None else None
        palette=pd.get('paletteBindingId') if pd is not None else None
        # Preserve every page in the source XML, but only import top + main page.
        shutil.copyfile(actor_file,out/actor_file.name)
        scenes=[self.scene(f) for f in sorted((self.data/'vehicles'/vehicle).glob('*.i3d'))
                if not any(t in f.stem.lower() for t in ('_col','_lod'))]
        main_scene=None; bg_node=None
        for s in scenes:
            if palette in s['nodes']:
                main_scene=s;bg_node=s['nodes'][palette][0][0];break
        if main_scene is None:
            main_scene=max(scenes,key=lambda s:sum(w.get('bindingId') in s['nodes'] for w in widgets))
        used_scenes={main_scene['path']}; textures={}; missing=[]
        def node_for(binding):
            candidates=[main_scene]+[s for s in scenes if s is not main_scene]
            for s in candidates:
                if binding in s['nodes']:
                    used_scenes.add(s['path']);return s,s['nodes'][binding][0]
            return None,None
        def material_maps(s,node):
            result={}
            for mid in node.get('materialIds','').split():
                mat=s['materials'].get(mid)
                if mat is None:continue
                for tex in mat:
                    if tex.tag.endswith('map') or tex.tag in ('Texture','Normalmap'):
                        path=s['files'].get(tex.get('fileId'))
                        if path and path.suffix.lower()=='.dds':
                            result[tex.get('name',tex.tag)]=path
                            textures[str(path)]=self.blob(path)
            return result
        bg_maps=material_maps(main_scene,bg_node) if bg_node is not None else {}
        background=bg_maps.get('backgroundMap') or bg_maps.get('Texture')
        fields=[]; rotators=[]; source_nodes={}
        for ix,w in enumerate(widgets):
            s,pair=node_for(w.get('bindingId'))
            if pair is not None:
                node,matrix=pair
                source_nodes[w.get('name',str(ix))]={'scene':s['path'].name,'node':node.attrib,
                    'matrix':matrix}
                for n in node.iter(): material_maps(s,n)
            elif w.get('bindingId'):
                missing.append({'widget':w.get('name'),'bindingId':w['bindingId']})
            if w['type'] not in ('digits','rotator'):continue
            field=self.bindings(w)
            if 'text' in field and w.get('bindingId') in visibility:
                field.pop('constant',None);field['param']=visibility[w['bindingId']]
            field.update(id=w.get('name',str(ix)),bindingId=w.get('bindingId'),
                         color=[float(w.get(c,defaults.get(c,.8))) for c in ('r','g','b')]+[1],
                         align=w.get('align','center'),font=w.get('font',defaults.get('font','GENERIC')))
            for prefix,key in [('h','highColor'),('l','lowColor')]:
                if any(c+prefix in w for c in 'rgb'):
                    field[key]=[float(w.get(c+prefix,w.get(c,1))) for c in 'rgb']+[1]
            if pair is not None:
                node,matrix=pair
                # Projection uses the font mesh's local X/Y axes in its own scene.
                shape=next(iter(node.findall('.//Shape')),node)
                if shape is not node:
                    # The digit mesh is generally the direct child of its binding.
                    sm=mul(matrix,transform(shape))
                else: sm=matrix
                source_nodes[w.get('name',str(ix))]['digitShape']=shape.get('name')
                field['_position']=[matrix[i][3] for i in range(3)]
                field['_axisX']=[sm[i][0] for i in range(3)]
                field['_axisY']=[sm[i][1] for i in range(3)]
                field['_scene']=s['path'].name
            if w['type']=='digits':fields.append(field)
            else:
                field['calibration']={k:v for k,v in w.items() if k.endswith('Angle') or k.endswith('Value')}
                rotators.append(field)

        root_ref=next(c for c in actor.findall('./components/component') if c.get('type')=='i3dComponent').find('i3dFile').get('file')
        root_name=Path(root_ref).name.lower()
        root_file=self.resolve(root_ref,actor_file.parent)
        if root_file:self.blob(root_file)
        for f in used_scenes:
            shutil.copyfile(f,out/f.name)
            self.blob(f)
            s=next(s for s in scenes if s['path']==f)
            # Analogue face artwork is often part of a general cockpit material,
            # separate from the needle's material. Keep those texture dependencies.
            if rotators:
                for name,pairs in s['nodes'].items():
                    if name and any(t in name.lower() for t in ('interior','gauge','dashboard')):
                        for node,_ in pairs:material_maps(s,node)
            shapes=f.with_suffix('.i3d.shapes')
            if self.copy_meshes and shapes.exists(): self.blob(shapes)
        # Copy scene dependencies for the main display material (including mask layers).
        if bg_node is not None: material_maps(main_scene,bg_node)
        self.blob(self.data/'shaders/str4_MotecShader.xml')
        has_artwork=any(k in bg_maps for k in ('backgroundMap','Texture','maskMap1','maskMap2'))
        reason=exclusion_reason({'id':vehicle,'widgets':widgets,'hasOriginalArtwork':has_artwork})
        if reason:
            return {'id':vehicle,'actor':str(actor_file.relative_to(self.game)).replace('\\','/'),
                'rootNames':[root_name],'mainPage':main.get('name') if main is not None else 'topPage',
                'defaults':defaults,'pageDefaults':dict(pd.attrib) if pd is not None else {},
                'widgets':widgets,'nodes':source_nodes,'textures':list(textures.values()),
                'background':str(background.relative_to(self.game)).replace('\\','/') if background else None,
                'scenes':[f.name for f in sorted(used_scenes)],'unresolvedBindings':missing,
                'layoutStatus':'excluded-original-assets-required','runtimeEnabled':False,'exclusionReason':reason,
                'geometry':None,'recreatedPrimary':False,'hasOriginalArtwork':has_artwork,
                'analogues':[w for w in widgets if w['type']=='rotator'],
                'profile':'profiles/'+vehicle+'.lua'}
        if bg_node is not None:
            material=main_scene['materials'][bg_node.get('materialIds').split()[0]]
            if 'maskMap1' in bg_maps or 'maskMap2' in bg_maps:
                im=compose(bg_maps,material,defaults,widgets,self.data/'shaders/str4_MotecShader.xml')
            elif background:im=Image.open(background).convert('RGBA')
            else:im=Image.new('RGBA',(1024,512),(10,13,16,255))
        elif background:
            im=Image.open(background).convert('RGBA')
        else:
            im=Image.new('RGBA',(1024,512),(10,13,16,255))
        width,height=im.size
        assets_dir='assets/vehicles/'+vehicle+'/'
        dest=self.output/assets_dir;dest.mkdir(parents=True,exist_ok=True)
        gauges,gauge_assets=fill_atlases(bg_maps,widgets,dest,width,height)
        self.project(fields,width,height,vehicle)
        crop={'x':0,'y':0,'width':width,'height':height};geometry_report=None
        geometry_file=ROOT/'catalog/geometry'/(vehicle+'__'+main_scene['path'].name+'.xml')
        if palette and geometry_file.exists():
            try:
                crop,geometry_report,surface=layout(fields,source_nodes,main_scene['path'].name,palette,load_nodes(geometry_file),width,height)
                cropped=im.crop((crop['x'],crop['y'],crop['x']+crop['width'],crop['y']+crop['height']))
                im=Image.new('RGBA',(width,height));im.paste(cropped,(0,0))
            except (KeyError,ValueError) as ex:
                geometry_report={'error':str(ex)}
        save_dds(im,dest/'background.dds')
        auxiliary=[]
        if geometry_report and 'error' not in geometry_report:
            outside=set(geometry_report['outsidePrimaryDisplay'])
            auxiliary=[f for f in fields if f['id'] in outside]
            fields=[f for f in fields if f['id'] not in outside]
        for f in fields+auxiliary: self.font(f['font'])
        profile={'id':vehicle,'name':vehicle.replace('_',' '),'rootNames':[root_name],
            'width':crop['width'],'height':crop['height']+40,'topPadding':40,'assetDirectory':assets_dir,
            'fontDirectory':'','deltaBar':False,'layoutStatus':'geometry-unverified' if geometry_report and 'error' not in geometry_report else 'draft-projection',
            'fields':fields,'auxiliaryFields':auxiliary,'clampText':True,
            'gauges':gauges,'shiftLights':self.lights(widgets,crop['width']),
            'assets':{'crop':crop,
                'background':{'file':'background.dds','width':width,'height':height},'gauges':gauge_assets}}
        # Use original fields for the tuned Supra, retain this complete extraction.
        manifest={'id':vehicle,'actor':str(actor_file.relative_to(self.game)).replace('\\','/'),
            'rootNames':[root_name],'mainPage':main.get('name') if main is not None else 'topPage',
            'defaults':defaults,'pageDefaults':dict(pd.attrib) if pd is not None else {},
            'widgets':widgets,'nodes':source_nodes,'textures':list(textures.values()),
            'background':str(background.relative_to(self.game)).replace('\\','/') if background else None,
            'scenes':[f.name for f in sorted(used_scenes)],'unresolvedBindings':missing,
            'layoutStatus':'hand-tuned' if vehicle=='Toyota_Supra_GT4' else profile['layoutStatus'],
            'geometry':geometry_report,'recreatedPrimary':False,'hasOriginalArtwork':has_artwork,
            'analogues':rotators,'profile':'profiles/'+vehicle+'.lua'}
        reason=exclusion_reason(manifest)
        manifest['runtimeEnabled']=reason is None
        if reason:manifest['exclusionReason']=reason;manifest['layoutStatus']='excluded-original-assets-required'
        if vehicle!='Toyota_Supra_GT4' and not reason:
            (out/'layout.json').write_text(json.dumps(profile,indent=2),encoding='utf-8')
            (self.output/'profiles'/f'{vehicle}.lua').write_text('-- Generated by tools/vehicle_catalog.py. Adjust catalog/calibrations.json, then rebuild.\n'
                +'DashboardMod.registerProfile('+lua(profile)+')\n',encoding='utf-8')
        return manifest

    def apply_tuning(self,fields,vehicle):
        tuning=self.calibrations.get(vehicle,{})
        for f in fields:
            f['x']=f['x']*tuning.get('scaleX',1)+tuning.get('offsetX',0)
            f['y']=f['y']*tuning.get('scaleY',1)+tuning.get('offsetY',0)
            f['height']*=tuning.get('heightScale',1)
            f.update(tuning.get('fields',{}).get(f['id'],{}))

    def project(self, fields, width, height, vehicle):
        positions=[f for f in fields if '_position' in f]
        if not positions:return
        # Dominant plane is computed from the digit mesh axes, independent of the
        # car's global orientation. It is an estimate until calibrated explicitly.
        dominant=max(positions,key=lambda f:sum(1 for g in positions if g['_scene']==f['_scene']))
        def normal(v):
            n=math.sqrt(sum(a*a for a in v));return [a/n for a in v] if n>1e-12 else [1,0,0]
        ax=normal(dominant['_axisX']);ay=normal(dominant['_axisY'])
        def dot(a,b):return sum(x*y for x,y in zip(a,b))
        xs=[dot(f['_position'],ax) for f in positions];ys=[dot(f['_position'],ay) for f in positions]
        xmin,xmax=min(xs),max(xs);ymin,ymax=min(ys),max(ys)
        sx=.76*width/max(xmax-xmin,1e-6);sy=.70*height/max(ymax-ymin,1e-6)
        for i,f in enumerate(fields):
            if '_position' in f:
                x=dot(f['_position'],ax);y=dot(f['_position'],ay)
                f['x']=(x-xmin)*sx+.12*width;f['y']=height*.86-(y-ymin)*sy
                f['height']=max(12,min(height*.22,math.sqrt(sum(v*v for v in f['_axisY']))*sy*2))
            else:
                f['x']=width*.15+(i%5)*width*.17;f['y']=height*.15+(i//5)*height*.12;f['height']=height*.04
            for k in list(f):
                if k.startswith('_'): del f[k]

    def lights(self, widgets, width):
        result=[]
        lights=[w for w in widgets if w['type']=='shiftlights']
        for i,w in enumerate(lights):
            fraction=None;threshold=None;color=[1,.1,.1,1]
            for key,c in [('greenT',[.1,1,.2,1]),('amberT',[1,.65,.05,1]),('redT',[1,.1,.1,1]),('blueT',[.1,.3,1,1])]:
                if key in w:
                    parts=w[key].split('/')
                    fraction=float(parts[0])/float(parts[1]) if len(parts)==2 else None
                    if len(parts)==1:threshold=float(parts[0])
                    color=c;break
            result.append({'x':width*(.25+.5*i/max(1,len(lights))), 'y':12,'width':width*.4/max(1,len(lights)),
                           'height':15,'fraction':fraction if fraction is not None else 1,'color':color})
            if threshold is not None:result[-1]['threshold']=threshold
        return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game',type=Path,default=DEFAULT_GAME)
    parser.add_argument('--output',type=Path,default=ROOT)
    parser.add_argument('--no-meshes',action='store_true',help='Skip binary geometry copies (smaller, incomplete offline archive)')
    parser.add_argument('--vehicle',action='append',help='Rebuild an exact vehicle ID; repeat for more cars')
    args=parser.parse_args()
    args.game=args.game.resolve();args.output=args.output.resolve()
    imp=Importer(args.game,args.output,not args.no_meshes)
    (args.output/'profiles').mkdir(parents=True,exist_ok=True)
    existing=args.output/'catalog/vehicles.json'
    rows=json.loads(existing.read_text()) if args.vehicle and existing.exists() else []
    for f in sorted((args.game/'data/vehicles').rglob('*actor.xml')):
        actor=ET.parse(f).getroot()
        if not any(c.get('type')=='MotecComponent' for c in actor.findall('./components/component')):continue
        id=f.relative_to(args.game/'data/vehicles').parts[0]
        if args.vehicle and id not in args.vehicle:continue
        row=imp.import_car(f);rows=[r for r in rows if r['id']!=id];rows.append(row)
        print(row['id'],len(row['widgets']),'widgets',len(row['unresolvedBindings']),'unresolved',flush=True)
    rows.sort(key=lambda r:r['id'])
    (args.output/'catalog/vehicles.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    old_files=args.output/'catalog/files.json'
    files={r['source']:r for r in json.loads(old_files.read_text())} if args.vehicle and old_files.exists() else {}
    files.update({r['source']:r for r in imp.blobs.values()})
    old_fonts=args.output/'assets/fonts/metadata.lua'
    if args.vehicle and old_fonts.exists():
        from lupa import LuaRuntime
        engine=LuaRuntime();engine.execute('DashboardMod={}')
        engine.execute(old_fonts.read_text())
        for name in engine.globals().DashboardMod.fonts.keys():imp.font(name)
        files.update({r['source']:r for r in imp.blobs.values()})
    old_files.write_text(json.dumps(list(files.values()),indent=2),encoding='utf-8')
    (args.output/'assets/fonts').mkdir(parents=True,exist_ok=True)
    (args.output/'assets/fonts/metadata.lua').write_text('DashboardMod.fonts='+lua(imp.fonts)+'\n',encoding='utf-8')
    entries=[{'id':r['id'],'file':r['profile'],'rootNames':r['rootNames']} for r in rows if r['id']!='Toyota_Supra_GT4' and not exclusion_reason(r)]
    (args.output/'catalog/vehicles.lua').write_text('DashboardMod.excludedVehicles='+lua({r['id']:exclusion_reason(r) for r in rows if exclusion_reason(r)})+'\nDashboardMod.catalog='+lua(entries)+'\n',encoding='utf-8')
    print(f'{len(rows)} vehicles; {len(files)} archived files; '+str(round(sum(p['bytes'] for p in files.values())/1024**2,1))+' MiB')


if __name__=='__main__':main()
