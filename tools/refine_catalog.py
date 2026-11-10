"""Reapply geometry and field calibration without re-extracting textures.

Use after adjusting catalog/calibrations.json. Does not touch hand-tuned profiles.
"""
from pathlib import Path
import json
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from lupa import LuaRuntime,lua_type
from vehicle_catalog import lua
from dash_geometry import load_nodes,layout
from dash_bounds import layout_bounds
from catalog_policy import exclusion_reason


def python(value):
    if lua_type(value)!='table':return value
    keys=list(value.keys())
    if keys and all(isinstance(k,int) for k in keys):return [python(value[i]) for i in range(1,len(keys)+1)]
    return {k:python(v) for k,v in value.items()}


def refine(vehicles=None):
    rows=json.loads((ROOT/'catalog/vehicles.json').read_text())
    tuning=json.loads((ROOT/'catalog/calibrations.json').read_text())
    engine=LuaRuntime();engine.execute('DashboardMod={registerProfile=function(p) imported=p end}')
    refined=0
    for row in rows:
        if vehicles and row['id'] not in vehicles:continue
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
                if not path.exists():continue
                nodes=load_nodes(path)
                if palette not in nodes:continue
                try:
                    _,report,_=layout(fields,row['nodes'],scene,palette,nodes,p['assets']['background']['width'],p['assets']['background']['height'])
                except ValueError:
                    bounds=ROOT/'inspection/live-catalog/bounds'/path.name
                    if not bounds.exists():raise
                    _,report=layout_bounds(fields,row['nodes'],scene,palette,load_nodes(bounds),p['assets']['background']['width'],p['assets']['background']['height'],tuning.get(row['id'],{}).get('screen',{}))
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
            if (f['id'] in outside and not c.get('includeInPrimary',False)) or (config.get('onlyConfiguredFields') and f['id'] not in config.get('fields',{})):p['auxiliaryFields'].append(f)
            else:primary.append(f)
        p['fields']=primary;p['clampText']=True
        p['layoutStatus']=config.get('layoutStatus',p['layoutStatus'])
        if 'paletteControls' in config:p['paletteControls']=config['paletteControls']
        if 'paletteAtlas' in config:p['assets']['palette']=config['paletteAtlas']
        if 'fonts' in config:p['fonts']=config['fonts']
        if 'shiftLights' in config:p['shiftLights']=config['shiftLights']
        if 'shiftLightConfig' in config:p['shiftLightConfig']=config['shiftLightConfig']
        if 'topPadding' in config:
            p['topPadding']=config['topPadding']
            p['height']=p['assets']['crop']['height']+p['topPadding']
        if config.get('displayCrop'):
            p['assets']['crop']=config['displayCrop']
            p['width']=p['assets']['crop']['width'];p['height']=p['assets']['crop']['height']+p['topPadding']
        row['layoutStatus']=p['layoutStatus']
        row['primaryDigits']=len(primary);row['auxiliaryDigits']=len(p['auxiliaryFields'])
        file.write_text('-- Generated profile. Refine through catalog/calibrations.json.\nDashboardMod.registerProfile('+lua(p)+')\n')
        refined+=1
    (ROOT/'catalog/vehicles.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    print('Refined',refined,'asset-based profiles; preserved the hand-tuned Supra and DLC V8 Supercars')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vehicle',action='append',help='Refine only an exact vehicle ID; repeat for more cars')
    args=parser.parse_args();refine(set(args.vehicle) if args.vehicle else None)
