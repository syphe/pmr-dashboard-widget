"""Build missing active digital dashboards from the local mounted-resource capture.

Development only: shipped runtime assets never require this importer.
"""
from pathlib import Path
import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from lupa import LuaRuntime
from vehicle_catalog import Importer,lua
from refine_catalog import python,refine
from catalog_policy import DIGITAL_ONLY

CAPTURE=ROOT/'inspection/live-catalog'
STAGE=ROOT/'.tools/captured-game'
RECOVER={'Mazda_787B_1991','Toyota_GT-One_TS020'}


def catalogue():return json.loads((ROOT/'catalog/game-vehicles.json').read_text(encoding='utf-8'))


def candidates():
    rows=json.loads((ROOT/'catalog/vehicles.json').read_text())
    complete={r['id'] for r in rows if r.get('runtimeEnabled')}
    complete.update({'Toyota_Supra_GT4','Ford_Mustang_V8Supercar_2024','Chevrolet_Camaro_V8Supercar_2024'})
    return [r for r in catalogue() if r['active'] and (r['vehicleId'] not in complete or not (ROOT/'profiles'/(r['vehicleId']+'.lua')).exists())]


def stage_capture():
    entries=json.loads((CAPTURE/'asset-manifest.json').read_text())
    defs={r['vehicleId']:r for r in catalogue()}
    count=0
    for entry in entries:
        if not entry['success']:continue
        source=entry['source'];parts=source.split('/')
        if parts[0].lower() not in {'data','datas','dlcs'}:raise ValueError('Nonofficial source: '+source)
        targets=[STAGE/source]
        # The existing importer indexes actor folders beneath data/vehicles.
        if 'vehicles' in parts and entry['vehicle'] in defs:
            root=parts.index('vehicles')
            targets.append(STAGE/'data/vehicles'/defs[entry['vehicle']]['vehicleId']/Path(*parts[root+2:]))
        original=CAPTURE/entry['destination']
        for target in targets:
            if target.exists():continue
            target.parent.mkdir(parents=True,exist_ok=True);os.link(original,target);count+=1
    print(f'Prepared {count} read-only source links',flush=True)


def prepare_geometry():
    stage_capture();jobs=[]
    for row in candidates():
        id=row['vehicleId'];path=STAGE/'data/vehicles'/id
        actor=ET.parse(next((path/'data').glob('*actor.xml'))).getroot()
        component=next(c for c in actor.findall('./components/component') if c.get('type')=='MotecComponent')
        widgets=list(component.findall('.//widget'))
        if any(w.get('type')=='rotator' for w in widgets) and id not in DIGITAL_ONLY:continue
        bindings={v for n in component.iter() for k,v in n.attrib.items() if k.endswith('BindingId') or k=='bindingId'}
        for scene in sorted(path.glob('*.i3d')):
            output=id+'__'+scene.name+'.xml'
            if (ROOT/'catalog/geometry'/output).exists():continue
            doc=ET.parse(scene).getroot()
            if not any(n.get('name') in bindings for n in doc.findall('.//Scene//*')):continue
            shapes=doc.find('Shapes')
            if shapes is None or not shapes.get('externalShapesFile'):continue
            mesh=scene.parent/shapes.get('externalShapesFile')
            if not mesh.exists():raise FileNotFoundError(mesh)
            shapes.set('externalShapesFile',mesh.as_posix())
            # Geometry export needs no game shaders, materials or textures.
            files=doc.find('Files')
            if files is not None:files.clear()
            for material in doc.findall('./Materials/Material'):
                attrs={k:material.get(k) for k in ('name','materialId')}
                material.clear();material.attrib.update(attrs);material.set('diffuseColor','1 1 1 1')
            destination=ROOT/'.tools/geometry-scenes'/id/scene.name
            destination.parent.mkdir(parents=True,exist_ok=True)
            ET.ElementTree(doc).write(destination,encoding='utf-8',xml_declaration=True)
            jobs.append({'file':destination.as_posix(),'output':output})
    (ROOT/'tools/editor_geometry_jobs.lua').write_text('DashboardGeometryJobs='+lua(jobs)+'\n',encoding='utf-8')
    print(f'Prepared {len(jobs)} scene geometry jobs',flush=True)


def prepare_bounds():
    """Use ordinary mounted-resource bounds when the editor cannot read UVs."""
    engine=LuaRuntime();engine.execute((ROOT/'tools/editor_geometry_jobs.lua').read_text())
    entries=json.loads((CAPTURE/'asset-manifest.json').read_text())
    active={r['vehicleId'] for r in catalogue() if r['active']}
    jobs=[]
    for _,job in engine.globals().DashboardGeometryJobs.items():
        path=Path(job.file);id=path.parent.name
        if id not in active:continue
        entry=next(e for e in entries if e['success'] and e['vehicle']==id and e['source'].endswith('/'+path.name))
        jobs.append({'file':entry['source'],'output':job.output,'active':True})
    (ROOT/'inspection/.live-bounds-jobs.lua').write_text('DashboardBoundsJobs='+lua(jobs)+'\n',encoding='utf-8')
    print(f'Prepared {len(jobs)} active mounted scenes; source inspection/capture-dashboard-bounds.lua in the game',flush=True)


class CapturedImporter(Importer):
    def resolve(self,ref,base):
        ref=ref.replace('\\','/').lstrip('$')
        path=self.game/ref if ref.split('/')[0].lower() in {'data','datas','dlcs'} else base/ref
        if path.exists():return path
        if path.suffix.lower() in ('.png','.tga','.jpg') and path.with_suffix('.dds').exists():return path.with_suffix('.dds')
        return None


def build():
    stage_capture()
    exclusions=json.loads((ROOT/'catalog/exclusions.json').read_text())
    for id in RECOVER:exclusions.pop(id,None)
    rows=json.loads((ROOT/'catalog/vehicles.json').read_text())
    importer=CapturedImporter(STAGE,ROOT,copy_meshes=False)
    engine=LuaRuntime();engine.execute('DashboardMod={}')
    engine.execute((ROOT/'assets/fonts/metadata.lua').read_text())
    importer.fonts=python(engine.globals().DashboardMod.fonts)
    # Policy reads the authored file, so publish the two original-art recoveries first.
    (ROOT/'catalog/exclusions.json').write_text(json.dumps(exclusions,indent=2)+'\n',encoding='utf-8')
    built=[]
    for row in candidates():
        id=row['vehicleId'];path=STAGE/'data/vehicles'/id
        actor_file=next((path/'data').glob('*actor.xml'))
        actor=ET.parse(actor_file).getroot()
        component=next(c for c in actor.findall('./components/component') if c.get('type')=='MotecComponent')
        selected=list(component.find('pages').findall('topPage'))+list(component.find('pages').findall('page'))[:1]
        widgets=[w for page in selected for w in page.findall('.//widget')]
        if any(w.get('type')=='rotator' for w in widgets) and id not in DIGITAL_ONLY:
            exclusions[id]='Analogue cluster excluded by user preference.'
            print('Excluded analogue '+id,flush=True);continue
        result=importer.import_car(actor_file)
        if not result.get('runtimeEnabled'):raise ValueError(f'{id}: '+result.get('exclusionReason','No original artwork'))
        if result['unresolvedBindings']:raise ValueError(f'{id}: unresolved bindings '+str(result['unresolvedBindings']))
        if result['layoutStatus'] not in {'geometry-unverified','bounds-unverified'}:raise ValueError(f'{id}: geometry mapping failed: '+str(result['geometry']))
        result['activeCapture']=True
        result['actor']=row['actorFile']
        rows=[r for r in rows if r['id']!=id];rows.append(result);built.append(id)
        # Keep a completed import resumable if a later vehicle fails.
        (ROOT/'catalog/vehicles.json').write_text(json.dumps(sorted(rows,key=lambda r:r['id']),indent=2),encoding='utf-8')
        (ROOT/'assets/fonts/metadata.lua').write_text('DashboardMod.fonts='+lua(importer.fonts)+'\n',encoding='utf-8')
        print('Built '+id+' '+result['layoutStatus'],flush=True)
    # Existing profiles and tuned V8 Supercars are preserved exactly.
    (ROOT/'catalog/vehicles.json').write_text(json.dumps(sorted(rows,key=lambda r:r['id']),indent=2),encoding='utf-8')
    (ROOT/'catalog/exclusions.json').write_text(json.dumps(dict(sorted(exclusions.items())),indent=2)+'\n',encoding='utf-8')
    (ROOT/'assets/fonts/metadata.lua').write_text('DashboardMod.fonts='+lua(importer.fonts)+'\n',encoding='utf-8')
    manual={'Toyota_Supra_GT4','Ford_Mustang_V8Supercar_2024','Chevrolet_Camaro_V8Supercar_2024'}
    entries=[{'id':r['id'],'file':r['profile'],'rootNames':r['rootNames']} for r in rows
             if r['id'] not in manual and r['id'] not in exclusions and (ROOT/r['profile']).exists()]
    (ROOT/'catalog/vehicles.lua').write_text('DashboardMod.excludedVehicles='+lua(exclusions)+'\nDashboardMod.catalog='+lua(entries)+'\n',encoding='utf-8')
    if built:refine(set(built))
    print(f'Built {len(built)} profiles; {len(exclusions)} excluded analogue clusters',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['geometry','bounds','build'])
    args=parser.parse_args()
    if args.action=='geometry':prepare_geometry()
    elif args.action=='bounds':prepare_bounds()
    else:build()


if __name__=='__main__':main()
