"""Estimate a rectangular screen from mounted geometry bounds, without UVs.

This is explicitly unverified: the sphere does not reveal the UV crop or screen
aspect. Per-vehicle calibration can override the inferred aspect and crop.
"""
import math
from dash_geometry import dot


def vector(node,key):return list(map(float,node.get(key).split()))
def length(v):return math.sqrt(dot(v,v))
def unit(v):return [x/length(v) for x in v]


def layout_bounds(fields,source_nodes,scene,palette,nodes,width,height,tuning):
    panel=nodes[palette]
    center=vector(panel,'sphereCenter')
    radius=vector(panel,'localSphere')[3]
    candidates=[source_nodes[f['id']] for f in fields if f['id'] in source_nodes and source_nodes[f['id']]['scene']==scene]
    if not candidates:raise ValueError('No digit orientation for mounted screen')
    entry=candidates[0]
    shape=nodes.get(entry.get('digitShape'),nodes[entry['node']['name']])
    ax,ay=unit(vector(shape,'axisX')),unit(vector(shape,'axisY'))
    aspect=tuning.get('aspect',width/height)
    # All captured display surfaces have unit scale. Reject other scales until
    # explicitly calibrated rather than silently treating a local radius as world.
    if any(abs(length(vector(panel,k))-1)>.001 for k in ('axisX','axisY')):
        raise ValueError('Non-unit mounted screen scale requires calibration')
    screen_h=2*radius/math.sqrt(1+aspect*aspect);screen_w=screen_h*aspect
    crop=tuning.get('crop',{'x':0,'y':0,'width':width,'height':height})
    report={'method':'mounted-bounding-sphere','uvsAvailable':False,'placed':[],'outsidePrimaryDisplay':[],
            'assumedAspect':aspect,'radiusMetres':radius}
    for f in fields:
        entry=source_nodes.get(f['id'])
        if not entry or entry['scene']!=scene or f.get('bindingId') not in nodes:
            report['outsidePrimaryDisplay'].append(f['id']);continue
        node=nodes[f['bindingId']]
        delta=[a-b for a,b in zip(vector(node,'origin'),center)]
        f['x']=crop['x']+crop['width']*(.5+dot(delta,ax)/screen_w)
        f['y']=crop['y']+crop['height']*(.5-dot(delta,ay)/screen_h)
        glyph=nodes.get(entry.get('digitShape'),node)
        # Shipped digit meshes use a unit-high quad; this is verified against
        # readable base-game geometry. Inherited scale supplies character size.
        f['height']=length(vector(glyph,'axisY'))*crop['height']/screen_h
        if not (crop['x']-5<=f['x']<=crop['x']+crop['width']+5 and crop['y']-5<=f['y']<=crop['y']+crop['height']+5):
            report['outsidePrimaryDisplay'].append(f['id'])
        else:report['placed'].append(f['id'])
    return crop,report
