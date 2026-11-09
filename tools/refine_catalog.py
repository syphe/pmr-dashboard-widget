"""Reapply geometry and field calibration without re-extracting textures.

Use after adjusting catalog/calibrations.json. Does not touch hand-tuned profiles.
"""
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from lupa import LuaRuntime,lua_type
from vehicle_catalog import lua
from dash_geometry import load_nodes,layout
from catalog_policy import exclusion_reason


def python(value):
    if lua_type(value)!='table':return value
    keys=list(value.keys())
    if keys and all(isinstance(k,int) for k in keys):return [python(value[i]) for i in range(1,len(keys)+1)]
    return {k:python(v) for k,v in value.items()}


def refine():
    rows=json.loads((ROOT/'catalog/vehicles.json').read_text())
    tuning=json.loads((ROOT/'catalog/calibrations.json').read_text())
    engine=LuaRuntime();engine.execute('DashboardMod={registerProfile=function(p) imported=p end}')
    for row in rows:
        if exclusion_reason(row):continue
        if row['id']=='Toyota_Supra_GT4':continue
        file=ROOT/row['profile']
        baseline=ROOT/'catalog/sources'/row['id']/'layout.json'
        if baseline.exists():p=json.loads(baseline.read_text())
        else:
            engine.execute(file.read_text());p=python(engine.globals().imported)
            baseline.write_text(json.dumps(p,indent=2),encoding='utf-8')
        # Lua's empty tables need their intended array types restored explicitly.
        for key in ('fields','gauges','shiftLights','auxiliaryFields'):
            if not p.get(key):p[key]=[]
        fields=p['fields']+p['auxiliaryFields'];p['auxiliaryFields']=[]
        palette=row['pageDefaults'].get('paletteBindingId')
        report=None
        if palette:
            for scene in row['scenes']:
                path=ROOT/'catalog/geometry'/(row['id']+'__'+scene+'.xml')
                nodes=load_nodes(path)
                if palette not in nodes:continue
                _,report,_=layout(fields,row['nodes'],scene,palette,nodes,p['assets']['background']['width'],p['assets']['background']['height'])
                row['geometry']=report
                break
        config=tuning.get(row['id'],{})
        outside=set(report['outsidePrimaryDisplay']) if report else set()
        original={w['name']:w for w in row['widgets']}
        primary=[]
        for f in fields:
            c=config.get('fields',{}).get(f['id'],{})
            f['x']=f['x']*config.get('scaleX',1)+config.get('offsetX',0)
            f['y']=f['y']*config.get('scaleY',1)+config.get('offsetY',0)
            f['height']*=config.get('heightScale',1)
            f.update(c)
            if original.get(f['id'],{}).get('zeroNeutral')=='true':f['zeroNeutral']=True
            if f['id'] in outside and not c.get('includeInPrimary',False):p['auxiliaryFields'].append(f)
            else:primary.append(f)
        p['fields']=primary;p['clampText']=True
        row['layoutStatus']=p['layoutStatus']
        row['primaryDigits']=len(primary);row['auxiliaryDigits']=len(p['auxiliaryFields'])
        file.write_text('-- Generated profile. Refine through catalog/calibrations.json.\nDashboardMod.registerProfile('+lua(p)+')\n')
    (ROOT/'catalog/vehicles.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    print('Refined',sum(not exclusion_reason(r) and r['id']!='Toyota_Supra_GT4' for r in rows),'asset-based profiles; preserved the hand-tuned Supra and DLC Mustang')


if __name__=='__main__':refine()
