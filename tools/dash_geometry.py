"""Fit the editor-exported display surface to its texture coordinates."""
import math
import xml.etree.ElementTree as ET


def solve(matrix, values):
    a=[list(row)+[v] for row,v in zip(matrix,values)]
    for col in range(len(a)):
        pivot=max(range(col,len(a)),key=lambda i:abs(a[i][col]))
        a[col],a[pivot]=a[pivot],a[col]
        scale=a[col][col]
        if abs(scale)<1e-14:raise ValueError('Degenerate texture mapping')
        a[col]=[x/scale for x in a[col]]
        for row in range(len(a)):
            if row==col:continue
            scale=a[row][col]
            a[row]=[x-scale*y for x,y in zip(a[row],a[col])]
    return [row[-1] for row in a]


def points(node):
    data=list(map(float,node.get('positions','').split()))
    return [data[i:i+3] for i in range(0,len(data),3)]


def dot(a,b):return sum(x*y for x,y in zip(a,b))


class Surface:
    def __init__(self, node):
        self.vertices=points(node)
        uv=list(map(float,node.get('uv','').split()))
        self.uv=[uv[i:i+2] for i in range(0,len(uv),2)]
        if len(self.uv)!=len(self.vertices) or len(self.uv)<3:raise ValueError('Missing UV data')
        # Fit 3D = origin + U*u + V*v, then invert the two surface axes.
        samples=[[1,*p] for p in self.uv]
        normal=[[sum(p[i]*p[j] for p in samples) for j in range(3)] for i in range(3)]
        coefficients=[solve(normal,[sum(p[j]*v[k] for p,v in zip(samples,self.vertices)) for j in range(3)]) for k in range(3)]
        self.origin=[c[0] for c in coefficients];self.u=[c[1] for c in coefficients];self.v=[c[2] for c in coefficients]
        uu,uv,vv=dot(self.u,self.u),dot(self.u,self.v),dot(self.v,self.v)
        self.inverse=((vv,-uv),(-uv,uu));self.determinant=uu*vv-uv*uv
        if abs(self.determinant)<1e-20:raise ValueError('Degenerate surface')
        self.error=max(math.dist(p,self.world(*q)) for p,q in zip(self.vertices,self.uv))

    def world(self,u,v):return [o+a*u+b*v for o,a,b in zip(self.origin,self.u,self.v)]

    def project(self,p):
        delta=[a-b for a,b in zip(p,self.origin)];x,y=dot(delta,self.u),dot(delta,self.v)
        return ((self.inverse[0][0]*x+self.inverse[0][1]*y)/self.determinant,
                (self.inverse[1][0]*x+self.inverse[1][1]*y)/self.determinant)


def load_nodes(path):
    return {n.get('name'):n for n in ET.parse(path).getroot()}


def layout(fields, source_nodes, scene, palette, nodes, width, height):
    """Mutate fields with native positions/sizes; return used UV crop and report."""
    surface=Surface(nodes[palette])
    us=[p[0] for p in surface.uv];vs=[p[1] for p in surface.uv]
    crop={'x':max(0,math.floor(min(us)*width)), 'y':max(0,math.floor((1-max(vs))*height)),
          'width':min(width,math.ceil(max(us)*width))-max(0,math.floor(min(us)*width)),
          'height':min(height,math.ceil((1-min(vs))*height))-max(0,math.floor((1-max(vs))*height))}
    report={'surfaceFitErrorMetres':surface.error,'placed':[],'outsidePrimaryDisplay':[]}
    for f in fields:
        entry=source_nodes.get(f['id'])
        if not entry or entry['scene']!=scene or f.get('bindingId') not in nodes:
            report['outsidePrimaryDisplay'].append(f['id']);continue
        node=nodes[f['bindingId']];pos=list(map(float,node.get('origin').split()))
        u,v=surface.project(pos);f['x'],f['y']=u*width,(1-v)*height
        # Match the source character mesh dimensions, including inherited scale.
        shape_name=entry.get('digitShape')
        verts=points(nodes[shape_name]) if shape_name in nodes else []
        if verts:
            projected=[surface.project(p) for p in verts]
            glyph_h=(max(v for _,v in projected)-min(v for _,v in projected))*height
            if glyph_h>0: f['height']=glyph_h
        if not (crop['x']-5<=f['x']<=crop['x']+crop['width']+5 and crop['y']-5<=f['y']<=crop['y']+crop['height']+5):
            report['outsidePrimaryDisplay'].append(f['id'])
        else:report['placed'].append(f['id'])
    return crop,report,surface
