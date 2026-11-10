"""Prepare mounted scene/live Motec audits and import their bounded captures.

No car switching, actor spawning, entitlement changes or layout tuning occurs.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import sys
import time
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
CAPTURE=ROOT/'inspection/runtime-audit'
sys.path.insert(0,str(ROOT/'.tools/python'))
from preview_catalog import runtime
from refine_catalog import python
from vehicle_catalog import lua


def canonical(element):
    return [element.tag,dict(sorted(element.attrib.items())),[canonical(c) for c in element]]


def motec(path):
    return next(c for c in ET.parse(path).findall('./components/component') if c.get('type')=='MotecComponent')


def prepare():
    engine=runtime();profiles=[p for _,p in engine.globals().DashboardMod.profiles.items()]
    catalogue={r['vehicleId']:r for r in json.loads((ROOT/'catalog/game-vehicles.json').read_text())}
    manifest=json.loads((ROOT/'inspection/live-catalog/asset-manifest.json').read_text())
    jobs=[]
    for p in profiles:
        id=p.id;row=catalogue[id]
        if not row['active']:continue
        actor=next(e for e in manifest if e['vehicle']==id and e['source'].lower().endswith('actor.xml') and e['success'])
        component=motec(ROOT/'inspection/live-catalog'/actor['destination'])
        pages=component.find('pages');main=pages.find('page')
        selected=list(pages.findall('topPage'))+([main] if main is not None else [])
        widgets=[{'page':page.get('name','TopPage'),'attributes':dict(w.attrib)} for page in selected for w in page.findall('.//widget')]
        names={w['attributes'][k] for w in widgets for k in w['attributes'] if k=='bindingId' or k.endswith('BindingId')}
        for page in selected:
            default=page.find('pagedefault')
            if default is not None and default.get('paletteBindingId'):names.add(default.get('paletteBindingId'))
        names.discard('pageSpecific')
        names.discard('')
        scenes=[]
        for entry in manifest:
            if entry['vehicle']!=id or not entry['success'] or not entry['source'].lower().endswith('.i3d'):continue
            doc=ET.parse(ROOT/'inspection/live-catalog'/entry['destination'])
            present=sorted({n.get('name') for n in doc.findall('.//Scene//*')} & names)
            if present:scenes.append({'file':entry['source'],'names':present})
        profile=python(p)
        # Lupa's empty table conversion is object-shaped; restore array intent.
        for key in ('fields','gauges','indicators','auxiliaryFields','paletteControls'):
            if not profile.get(key):profile[key]=[]
        jobs.append({'id':id,'catalogueId':row['catalogueId'],'actorFile':row['actorFile'],
                     'mainPage':main.get('name') if main is not None else None,
                     'profileSha256':hashlib.sha256((ROOT/'profiles'/(id+'.lua')).read_bytes()).hexdigest(),
                     'widgets':widgets,'bindingNames':sorted(names),'scenes':scenes,
                     'profile':{k:profile[k] for k in ('fields','gauges','indicators','auxiliaryFields','paletteControls')}})
    for folder in ('scenes','live','actors'):(CAPTURE/folder).mkdir(parents=True,exist_ok=True)
    (CAPTURE/'jobs.json').write_text(json.dumps(jobs,indent=2),encoding='utf-8')
    encoded=lua(jobs)
    (ROOT/'inspection/.live-audit-jobs.lua').write_text('DashboardAuditJobs='+encoded+'\n',encoding='utf-8')
    recorder=(ROOT/'inspection/runtime-dashboard-audit.lua').read_text(encoding='utf-8')
    revision=hashlib.sha256((encoded+recorder).encode('utf-8')).hexdigest()[:12]
    recorder_path=ROOT/'inspection'/('.live-audit-recorder-'+revision+'.lua')
    recorder_path.write_text(recorder,encoding='utf-8')
    loader=ROOT/'inspection'/('.live-audit-start-'+revision+'.lua')
    loader.write_text('DashboardAuditJobsOverride='+encoded+'\nsource('+lua(recorder_path.as_posix())+')\n',encoding='utf-8')
    (CAPTURE/'loader.txt').write_text(loader.as_posix(),encoding='utf-8')
    print(f'Prepared {len(jobs)} active digital profiles and {sum(len(j["scenes"]) for j in jobs)} unlinked scene inspections')
    print('Cache-safe console command: source('+lua(loader.as_posix())+')')


def read_capture(path):
    return json.loads(ET.parse(path).getroot().get('json'))


def check_live(job,record):
    """Report concrete differences, keeping unavailable lap samples as notes."""
    findings=[];notes=[]
    if record.get('schemaVersion')!=1 or record.get('complete') is not True:
        return ['Live capture incomplete'],notes
    if record.get('vehicleId')!=job['id']:return ['Live capture vehicle identity mismatch'],notes
    pages=record.get('pages',[])
    if not pages:return ['No live Motec pages captured'],notes
    actual={(p['name'],w['name']):w for p in pages for w in p.get('widgets',[])}
    for expected in job['widgets']:
        attrs=expected['attributes'];key=(expected['page'],attrs.get('name'))
        w=actual.get(key)
        if w is None:findings.append(f'Missing live widget: {key[0]}/{key[1]}');continue
        data=w.get('properties',{})
        for src,dst in [('type','type'),('vehicleParam','vehicleParam'),('bindingId','nodeName'),('font','fontName')]:
            if src in attrs and data.get(dst)!=attrs[src]:findings.append(f'{key[0]}/{key[1]}: {src} source={attrs[src]!r}, live={data.get(dst)!r}')
        if attrs.get('type')=='digits' and attrs.get('bindingId') not in (None,'pageSpecific') and not w.get('node'):
            findings.append(f'{key[0]}/{key[1]}: live digit node is unresolved')
    digits=[w for p in pages for w in p.get('widgets',[]) if w.get('properties',{}).get('type')=='digits']
    by_name={w['name']:w for w in digits}
    reads=record.get('readings',{})
    for field in job['profile']['fields']:
        id=field['id'];reading=reads.get('field:'+id)
        param=field.get('param') or ('speed' if field.get('method')=='getForwardSpeedKPH' else None)
        if reading is None:findings.append(f'{id}: profile reading not captured');continue
        if reading.get('getterAvailable') is False:findings.append(f'{id}: telemetry getter unavailable')
        if reading.get('error'):findings.append(f'{id}: {reading["error"]}')
        if reading.get('value') is None and not reading.get('error'):
            notes.append(f'{id}: no valid numeric sample in this session')
        widget=by_name.get(id)
        if not widget:
            candidates=[w for w in digits if field.get('bindingId') and w.get('properties',{}).get('nodeName')==field['bindingId']]
            if not candidates and param:candidates=[w for w in digits if w.get('properties',{}).get('vehicleParam')==param]
            if len(candidates)==1:widget=candidates[0]
        if widget:
            native=widget.get('properties',{})
            if field.get('font') and native.get('fontName')!=field['font']:findings.append(f'{id}: profile font differs from live font')
            alignment={'left':0,'center':1,'right':2}.get(field.get('align','right'))
            if native.get('align') is not None and native['align']!=alignment:findings.append(f'{id}: profile alignment differs from live alignment')
            for authored,live_key in [('high','highThreshold'),('low','lowThreshold')]:
                if authored in field and live_key in native and abs(field[authored]-native[live_key])>max(.0001,abs(native[live_key])*.00001):
                    findings.append(f'{id}: profile {authored} threshold differs from live threshold')
            # Compare output only when the native widget has a valid reading and
            # the source's actual parameter is the one the profile reads.
            text=native.get('updateText')
            if param==native.get('vehicleParam') and reading.get('value') is not None and isinstance(text,str) and text:
                formatted=reading.get('formatted')
                if isinstance(formatted,str) and formatted.replace('!','\u00b0')!=text.replace('!','\u00b0'):
                    def numeric(s):
                        parts=re.findall(r'[-+]?\d+(?:\.\d+)?',s)
                        if ':' in s and len(parts)==2:return float(parts[0])*60+float(parts[1])
                        return float(parts[0]) if len(parts)==1 else None
                    a,b=numeric(formatted),numeric(text)
                    precision=native.get('precision',0)
                    tolerance=max(2*10**(-precision),abs(b or 0)*.02)
                    if field.get('kind')=='gear' and formatted.strip()!=text.strip():
                        findings.append(f'{id}: gear/neutral text differs: profile {formatted!r}, native {text!r}')
                    elif a is not None and b is not None and abs(a-b)>tolerance:
                        findings.append(f'{id}: profile value {formatted!r} differs from native {text!r}; conversion/units need review')
                    else:notes.append(f'{id}: formatting differs: profile {formatted!r}, native {text!r}')
    for group,prefix in [('gauges','gauge:'),('indicators','indicator:'),('paletteControls','palette:')]:
        for binding in job['profile'].get(group,[]):
            reading=reads.get(prefix+binding['id'])
            if not reading or reading.get('getterAvailable') is False or reading.get('error'):
                findings.append(f'{group}/{binding["id"]}: telemetry read unavailable or failed')
    return sorted(set(findings)),sorted(set(notes))


def ingest():
    jobs=json.loads((CAPTURE/'jobs.json').read_text())
    previous=ROOT/'catalog/runtime-audit.json'
    old=json.loads(previous.read_text()).get('vehicles',{}) if previous.exists() else {}
    vehicles={}
    for job in jobs:
        id=job['id'];digest=hashlib.sha256((ROOT/'profiles'/(id+'.lua')).read_bytes()).hexdigest()
        # Never relabel evidence against changed profile definitions.
        if job['profileSha256']!=digest:continue
        row={'profileSha256':digest,'sceneAuditStatus':'pending','validationStatus':'pending-runtime-audit','findings':[],'notes':[]}
        scene_file=CAPTURE/'scenes'/(id+'.xml')
        if scene_file.exists():
            scene=read_capture(scene_file)
            if scene.get('profileSha256')==digest and scene.get('schemaVersion')==1:
                findings=list(scene.get('errors',[]))
                seen={name for s in scene.get('scenes',[]) for name in s.get('resolvedNames',[])}
                findings += ['Unresolved mounted binding: '+name for name in set(job['bindingNames'])-seen]
                captured=CAPTURE/'actors'/(id+'.xml')
                original=next((ROOT/'inspection/live-catalog/vehicles'/id/'data').glob('*actor.xml'),None)
                if not captured.exists():findings.append('Mounted actor definition not captured')
                elif original is None:findings.append('Original Motec baseline unavailable')
                elif canonical(motec(captured))!=canonical(motec(original)):findings.append('Mounted Motec definition differs from original source capture')
                row['sceneAuditStatus']='findings' if findings else 'passed'
                row['sceneFindings']=sorted(set(findings));row['scenesInspected']=len(scene.get('scenes',[]))
        live_file=CAPTURE/'live'/(id+'.xml')
        if live_file.exists():
            live=read_capture(live_file)
            if live.get('profileSha256')==digest:
                row['findings'],row['notes']=check_live(job,live)
                row['liveWidgetCount']=sum(len(p.get('widgets',[])) for p in live.get('pages',[]))
                row['validationStatus']='runtime-audit-findings' if row['findings'] or row['sceneAuditStatus']!='passed' else 'runtime-audited'
        elif old.get(id,{}).get('profileSha256')==digest and old[id].get('validationStatus')!='pending-runtime-audit':
            for key in ('validationStatus','findings','notes','liveWidgetCount'):row[key]=old[id].get(key,row.get(key))
            if row['sceneAuditStatus']!='passed':row['validationStatus']='runtime-audit-findings'
        vehicles[id]=row
    data={'schemaVersion':1,'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'vehicles':dict(sorted(vehicles.items()))}
    previous.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    text=['# Runtime dashboard audit','',
          'Capture method, layout calibration and runtime validation are independent. '
          '`runtime-audited` requires a matching current-profile capture of the actual player Motec component and telemetry getters, '
          'plus a passing mounted-scene/source comparison. It does not establish visual fidelity or full-range warning behaviour. '
          'Formatting differences and unavailable samples remain visible as notes.','',
          'The initial live Audi R8 LMS GT3 Evo audit exposed missing Pa-to-bar conversion. '
          'The native pressure helper returned 3.272 for 327200 Pa with the Motec override enabled. '
          'Fuel/oil pressure conversions were corrected in 35 profiles and in their generators; '
          'that correction does not mean all 35 cars have received live Motec audits.','',
          '| Vehicle | Mounted scenes | Live Motec | Findings |', '| --- | --- | --- | ---: |']
    for id,r in sorted(vehicles.items()):text.append(f'| `{id}` | {r["sceneAuditStatus"]} | {r["validationStatus"]} | {len(r["findings"])} |')
    for id,r in sorted(vehicles.items()):
        issues=r.get('sceneFindings',[])+r['findings']+r['notes']
        if issues:text+=['',f'## {id}','']+['- '+s for s in issues]
    (ROOT/'catalog/RUNTIME_AUDIT.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    print(f'Audit imported: {sum(r["sceneAuditStatus"]=="passed" for r in vehicles.values())}/{len(vehicles)} mounted-scene passes; '
          f'{sum(r["validationStatus"]=="runtime-audited" for r in vehicles.values())} live passes, '
          f'{sum(r["validationStatus"]=="runtime-audit-findings" for r in vehicles.values())} live audits with findings')


def watch(seconds):
    from preview_catalog import refresh_gallery
    from profile_coverage import main as coverage
    deadline=time.monotonic()+seconds;previous=None
    print(f'Watching local audit captures for {seconds:g} seconds',flush=True)
    while time.monotonic()<deadline and not (CAPTURE/'stop-watch').exists():
        inputs=list((CAPTURE/'live').glob('*.xml'))+list((CAPTURE/'scenes').glob('*.xml'))+list((ROOT/'profiles').glob('*.lua'))+[CAPTURE/'jobs.json']
        signature=tuple((p.as_posix(),p.stat().st_mtime_ns,p.stat().st_size) for p in sorted(inputs))
        if signature!=previous:
            try:
                ingest();coverage();refresh_gallery();previous=signature
                print('Refreshed audit report, coverage and gallery',flush=True)
            except (ET.ParseError,json.JSONDecodeError):
                print('Capture is still being written; retrying',flush=True)
        time.sleep(1)
    print('Audit watcher stopped',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['prepare','ingest','watch'])
    parser.add_argument('--seconds',type=float,default=3600,help='Bounded watcher lifetime (default: one hour)')
    args=parser.parse_args()
    if args.action=='prepare':prepare()
    elif args.action=='ingest':ingest()
    else:watch(max(0,args.seconds))
