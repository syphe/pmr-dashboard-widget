"""Process a live catalogue capture and plan dashboard dependency exports."""
from pathlib import Path, PurePosixPath
import argparse
import collections
import csv
import hashlib
import json
import posixpath
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
CAPTURE=ROOT/'inspection/live-catalog'


def is_mod_data(value):
    return isinstance(value,dict) and (bool(value.get('isMod') or value.get('modName'))
        or any(isinstance(v,str) and '/mods/' in v.replace('\\','/').lower() for v in value.values()))


def stock_definition(entry):
    # Strip custom livery records embedded inside otherwise official definitions.
    def clean(value):
        if isinstance(value,dict):return {k:clean(v) for k,v in value.items() if not is_mod_data(v)}
        if isinstance(value,list):return [clean(v) for v in value if not is_mod_data(v)]
        return value
    return clean(entry)


def official_definitions(rows):
    return [stock_definition(r) for r in rows if not is_mod_data(r['definition'])]


def vehicle_ids(definitions):
    return {r['definition']['vehicleRootPath'].replace('\\','/').split('/')[-1] for r in definitions}


def official_assets(rows,ids):
    return [r for r in rows if r['vehicle'] in ids|{'shared'}
            and re.match(r'^(?:datas?|dlcs)/',r['source'],re.I)]


def refresh(log):
    lines=log.read_text(encoding='utf-8',errors='replace').splitlines()
    def records(marker,subset=lines):
        return [json.loads(line.split(marker,1)[1]) for line in subset if marker in line]
    definitions=official_definitions(list({r['key']:r for r in records('VEHICLE_CAPTURE DEF ')}.values()))
    ids=vehicle_ids(definitions)
    timestamps=[line.split(' VEHICLE_CAPTURE BEGIN',1)[0] for line in lines if ' VEHICLE_CAPTURE BEGIN' in line]
    (CAPTURE/'capture-info.json').write_text(json.dumps({'capturedAt':timestamps[-1] if timestamps else None},indent=2),encoding='utf-8')
    # Ignore the unsuccessful initial directory-creation probe.
    starts=[i for i,line in enumerate(lines) if 'VEHICLE_ASSET_READY' in line]
    assets=lines[starts[-1]:] if starts else []
    for name,rows in [('definitions.json',definitions),
                      ('asset-manifest.json',official_assets(records('VEHICLE_ASSET ',assets),ids)),
                      ('car-assets.json',[r for r in records('VEHICLE_ASSET_CAR ',assets) if r['id'] in ids])]:
        (CAPTURE/name).write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
    print(f'Read {len(definitions)} catalogue entries from {log.name}')


def resolve(filename,source):
    filename=filename.replace('\\','/')
    if filename.startswith('$'):return posixpath.normpath(filename[1:])
    return posixpath.normpath(posixpath.join(posixpath.dirname(source),filename))


def plan():
    definitions=official_definitions(json.loads((CAPTURE/'definitions.json').read_text(encoding='utf-8')))
    ids=vehicle_ids(definitions)
    files=official_assets(json.loads((CAPTURE/'asset-manifest.json').read_text()),ids)
    cars={r['id']:r for r in json.loads((CAPTURE/'car-assets.json').read_text()) if r['id'] in ids}
    jobs={}
    def add(source,kind,id):
        if source.lower().endswith('.png'):source=source[:-4]+'.dds'
        # Only base-game and DLC mounted resources are capture dependencies.
        if source.split('/')[0].lower() not in {'data','datas','dlcs'}:return
        destination='resources/'+source
        if '..' in PurePosixPath(destination).parts:raise ValueError('Unsafe dependency path: '+source)
        key=source.lower()
        if key not in jobs:jobs[key]={'source':source,'destination':destination,'kind':kind,'vehicles':[]}
        if id not in jobs[key]['vehicles']:jobs[key]['vehicles'].append(id)
    actors={}
    for row in files:
        if row['success'] and row['source'].lower().endswith('actor.xml'):
            actors[row['vehicle']]=ET.parse(CAPTURE/row['destination']).getroot()
    scene_count=0
    for row in files:
        if not row['success'] or not row['source'].lower().endswith('.i3d'):continue
        id=row['vehicle'];actor=actors.get(id)
        if actor is None:continue
        motec=next((c for c in actor.findall('./components/component') if c.get('type')=='MotecComponent'),None)
        if motec is None:continue
        bindings={v.lower() for n in motec.iter() for k,v in n.attrib.items()
                  if k.lower().endswith('bindingid') and v.lower()!='pagespecific'}
        doc=ET.parse(CAPTURE/row['destination']).getroot()
        relevant=any(n.get('name','').lower() in bindings for n in doc.findall('.//Scene//*'))
        display=bool(re.search(r'display|motec|dashboard',PurePosixPath(row['source']).name,re.I))
        if not relevant and not display:continue
        scene_count+=1
        sourcefiles={n.get('fileId'):resolve(n.get('filename'),row['source']) for n in doc.findall('./Files/File')}
        shapes=doc.find('Shapes')
        if shapes is not None and shapes.get('externalShapesFile'):
            add(resolve(shapes.get('externalShapesFile'),row['source']),'shapes',id)
        material_ids=set()
        def walk(node,matched=False):
            matched=matched or node.get('name','').lower() in bindings
            if matched:material_ids.update(node.get('materialIds','').split())
            for child in node:walk(child,matched)
        scene=doc.find('Scene')
        if scene is not None:walk(scene)
        for material in doc.findall('./Materials/Material'):
            shader=sourcefiles.get(material.get('customShaderId'),'')
            selected=display or material.get('materialId') in material_ids or 'motec' in shader.lower()
            if selected:
                if shader:add(shader,'xml',id)
                for node in material:
                    file=sourcefiles.get(node.get('fileId'))
                    if file and file.lower().endswith(('.png','.dds')):add(file,'texture',id)
        # Analogue faces can be baked into cockpit art rather than a bound node.
        textures=cars.get(id,{}).get('textures',{})
        textures=textures.values() if isinstance(textures,dict) else textures
        for texture in textures:
            name=PurePosixPath(texture).name.lower()
            art=re.search(r'display|motec|dashboard|gauge|needle|instrument|lcd',name)
            cockpit=re.search(r'cockpit|interior|swheel',name) and re.search(r'alb|glow|emissive',name)
            if art or cockpit:add(texture,'texture',id)
    for source in ['data/shared/alphabet/fonts.xml','data/shared/alphabet/fontMaterialHolder.i3d']:
        add(source,'xml','shared')
    rows=sorted(jobs.values(),key=lambda r:r['source'].lower())
    (CAPTURE/'dependency-jobs.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    def quote(s):return '"'+s.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')+'"'
    lua=['-- Generated from captured scene references, not guessed resource names.', 'VehicleAssetCapture.jobs={']
    for row in rows:
        lua.append('{source='+quote(row['source'])+',destination='+quote(row['destination'])
                   +',kind='+quote(row['kind'])+',vehicle='+quote(row['vehicles'][0] if len(row['vehicles'])==1 else 'shared')+'},')
    lua+=['}', '''function VehicleAssetCapture.runJobs(first,last)
 local c=VehicleAssetCapture
 for i=first,math.min(last,#c.jobs) do
  local j=c.jobs[i];c.copy(j.source,c.root..j.destination,j.kind,j.vehicle)
 end
 print('VEHICLE_DEPENDENCIES_BATCH '..first..'-'..last..' total='..#c.jobs)
end''',f"print('VEHICLE_DEPENDENCIES_READY {len(rows)}')"]
    (ROOT/'inspection/.live-dependency-jobs.lua').write_text('\n'.join(lua)+'\n',encoding='utf-8')
    print(f'Planned {len(rows)} dependencies from {scene_count} dashboard/instrument scenes:',dict(collections.Counter(r['kind'] for r in rows)))


def report():
    definitions=official_definitions(json.loads((CAPTURE/'definitions.json').read_text(encoding='utf-8')))
    assets=official_assets(json.loads((CAPTURE/'asset-manifest.json').read_text()),vehicle_ids(definitions))
    by_vehicle=collections.Counter(r['vehicle'] for r in assets if r['success'] and r['destination'].startswith('vehicles/'))
    jobs=json.loads((CAPTURE/'dependency-jobs.json').read_text())
    copied={r['source'].lower() for r in assets if r['success']}
    dependency_counts=collections.Counter(id for j in jobs if j['source'].lower() in copied for id in j['vehicles'])
    dashboards={}
    for file in assets:
        if not file['success'] or not file['source'].lower().endswith('actor.xml'):continue
        doc=ET.parse(CAPTURE/file['destination']).getroot()
        component=next((c for c in doc.findall('./components/component') if c.get('type')=='MotecComponent'),None)
        if component is None:continue
        pages=component.find('pages')
        first=pages.find('page') if pages is not None else None
        top=pages.find('topPage') if pages is not None else None
        widgets=[dict(n.attrib) for page in (top,first) if page is not None for n in page.findall('.//widget')]
        defaults=component.find('default')
        dashboard={'defaults':dict(defaults.attrib) if defaults is not None else {},
                   'mainPage':dict(first.attrib) if first is not None else None,
                   'pageCount':len(pages.findall('page')) if pages is not None else 0,
                   'mainWidgets':widgets,'widgetTypes':dict(collections.Counter(w.get('type') for w in widgets))}
        dashboards[file['vehicle']]=dashboard
        (CAPTURE/'vehicles'/file['vehicle']/'dashboard.json').write_text(json.dumps(dashboard,indent=2),encoding='utf-8')
    (CAPTURE/'dashboards.json').write_text(json.dumps(dashboards,indent=2),encoding='utf-8')
    rows=[]
    for entry in definitions:
        d=entry['definition'];vehicle=d['vehicleRootPath'].replace('\\','/').split('/')[-1]
        group=d.get('entitlementId','Base game')
        rows.append({'vehicleId':vehicle,'catalogueId':d['ID'],'manufacturer':d['Manufacturer'],
                     'name':d['Name'],'year':d['Year'],'class':d['VehicleClass'],'package':group,
                     'active':d['Active'],'actorFile':d['ActorFile'],'vdefFile':d['vdefFile'],
                     'capturedDefinitionFiles':by_vehicle[vehicle],
                     'dashboardDependencyFiles':dependency_counts[vehicle],
                     'hasMotec':vehicle in dashboards,'bundledProfile':(ROOT/'profiles'/(vehicle+'.lua')).is_file()})
    rows.sort(key=lambda r:(r['package'],r['manufacturer'],str(r['name']),r['vehicleId']))
    (ROOT/'catalog/game-vehicles.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    with (ROOT/'catalog/game-vehicles.csv').open('w',encoding='utf-8-sig',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    groups=collections.defaultdict(list)
    for row in rows:groups[row['package']].append(row)
    captured_at=json.loads((CAPTURE/'capture-info.json').read_text()).get('capturedAt','unknown time')
    text=['# Live PMR vehicle catalogue','',
          f'Captured from the running game at {captured_at}: **{len(rows)} base-game and DLC cars**.',
          'Includes inactive definitions; an entry is not proof that the car is available to drive.',
          'IDs below are actor-folder IDs used by dashboard profiles; the CSV/JSON also preserve the separate catalogue IDs.',
          '', '| Package / entitlement key | Entries | Active |','| --- | ---: | ---: |']
    for group,items in groups.items():text.append(f'| {group} | {len(items)} | {sum(r["active"] for r in items)} |')
    success=[r for r in assets if r['success']]
    text+=['','## Asset capture','',
           f'{len(success)} successful resource exports; {len(assets)-len(success)} failed attempts.',
           'Raw files and the source/destination manifest are in `inspection/live-catalog/`.',
           'Actor, vehicle-definition and I3D XML were read and reserialized through PMR; they are not byte-identical copies.',
           'Textures and geometry binaries use the mounted-resource copy API. Resources were also readable for inactive catalogue entries; no Active flags or entitlements were changed, and no vehicle actors were spawned.',
           'Capture focuses on dashboard/instrument dependencies, not complete playable vehicle packages.']
    for group,items in groups.items():
        text+=['',f'## {group} ({len(items)})','', '| Manufacturer | Car | Year | Class | Actor-folder ID | Active |','| --- | --- | ---: | --- | --- | --- |']
        for r in items:
            text.append(f'| {r["manufacturer"]} | {r["name"]} | {r["year"]} | {r["class"]} | `{r["vehicleId"]}` | {"Yes" if r["active"] else "No"} |')
    (ROOT/'catalog/GAME_VEHICLES.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    inventory=[]
    for row in success:
        path=CAPTURE/row['destination']
        inventory.append({**row,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (CAPTURE/'verified-assets.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
    summary={'catalogueEntries':len(rows),'baseCars':sum(r['package']=='Base game' for r in rows),
             'dlcCars':sum(r['package']!='Base game' for r in rows),
             'activeCars':sum(r['active'] for r in rows),
             'successfulExports':len(inventory),'failedExports':len(assets)-len(inventory),
             'exportedBytes':sum(r['bytes'] for r in inventory),'dashboardDefinitions':len(dashboards),
             'exportKinds':dict(collections.Counter(r['kind'] for r in inventory))}
    (CAPTURE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(f'Wrote catalogue for {len(rows)} cars; verified {len(inventory)} exports ({sum(r["bytes"] for r in inventory)/1024**2:.1f} MiB)')


def verify():
    import struct
    files=json.loads((CAPTURE/'asset-manifest.json').read_text())
    jobs=json.loads((CAPTURE/'dependency-jobs.json').read_text())
    copied={row['source'].lower() for row in files if row['success']}
    missing=[job['source'] for job in jobs if job['source'].lower() not in copied]
    if missing:raise ValueError('Dependencies not copied: '+', '.join(missing))
    for row in files:
        if not row['success']:raise ValueError('Failed export: '+row['source'])
        path=(CAPTURE/row['destination']).resolve()
        if not path.is_relative_to(CAPTURE.resolve()):raise ValueError('Unsafe capture destination')
        if row['kind']=='xml':ET.parse(path)
        elif row['kind']=='texture':
            with path.open('rb') as file:header=file.read(128)
            if len(header)!=128 or header[:4]!=b'DDS ':raise ValueError('Invalid DDS: '+str(path))
            height,width=struct.unpack_from('<II',header,12)
            if not width or not height:raise ValueError('Empty texture: '+str(path))
        elif not path.stat().st_size:raise ValueError('Empty geometry file: '+str(path))
    definitions=json.loads((CAPTURE/'definitions.json').read_text(encoding='utf-8'))
    if official_definitions(definitions)!=definitions:raise ValueError('Vehicle mods or custom liveries remain in the catalogue')
    if official_assets(files,vehicle_ids(definitions))!=files:raise ValueError('Nonofficial assets remain in the capture')
    states={row['id']:row for row in json.loads((CAPTURE/'car-assets.json').read_text())}
    actors={row['vehicle'] for row in files if row['source'].lower().endswith('actor.xml')}
    for entry in definitions:
        d=entry['definition'];id=d['vehicleRootPath'].replace('\\','/').split('/')[-1]
        if states.get(id,{}).get('captureRequested',d['Active']) and id not in actors:
            raise ValueError('Missing requested actor definition: '+id)
    print(f'Validated {len(files)} exports: XML parsing, DDS headers, nonempty meshes, dependency coverage and requested-vehicle coverage')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['refresh','plan','report','verify'])
    parser.add_argument('--log',type=Path)
    args=parser.parse_args()
    CAPTURE.mkdir(parents=True,exist_ok=True)
    if args.action=='refresh':
        if not args.log:parser.error('--log is required for refresh')
        refresh(args.log)
    elif args.action=='plan':plan()
    elif args.action=='report':report()
    else:verify()


if __name__=='__main__':main()
