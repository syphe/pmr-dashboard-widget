"""Build private runtime assets from the user's installation. No game/editor needed.

Reads authored profiles; never regenerates them or needs captured geometry/XML.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from game_install import find_game_install


def python_value(value):
    from lupa import lua_type
    if lua_type(value)!='table':return value
    keys=list(value.keys())
    if keys and all(isinstance(k,int) for k in keys):return [python_value(value[i]) for i in range(1,len(keys)+1)]
    return {k:python_value(v) for k,v in value.items()}


def definitions(project):
    from lupa import LuaRuntime
    engine=LuaRuntime()
    engine.execute('DashboardMod={profiles={},registerProfile=function(p) table.insert(DashboardMod.profiles,p) end}')
    engine.execute((project/'catalog/vehicles.lua').read_text())
    entries=[{'id':'Toyota_Supra_GT4','file':'profiles/Toyota_Supra_GT4.lua'},
             {'id':'Ford_Mustang_V8Supercar_2024','file':'profiles/Ford_Mustang_V8Supercar_2024.lua'}]
    entries+=python_value(engine.globals().DashboardMod.catalog)
    for entry in entries:
        engine.execute((project/entry['file']).read_text())
    return {p['id']:p for p in python_value(engine.globals().DashboardMod.profiles)},entries


def builder(game,stage):
    from vehicle_catalog import Importer
    class RuntimeAssets(Importer):
        def __init__(self,game,output,copy_meshes=False):
            self.game=game.resolve();self.data=self.game/'data'
            self.output=output.resolve();self.fonts={}
        def blob(self,path):
            # Font preparation needs provenance, not an extra copy of game data.
            return {'source':path.resolve().relative_to(self.game).as_posix(),
                    'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    return RuntimeAssets(game,stage,copy_meshes=False)


def build_dashboard(imp,profile,actor_file):
    from PIL import Image
    from dash_material import compose
    from dash_gauges import fill_atlases
    from dds import save_dds
    actor=ET.parse(actor_file).getroot()
    motec=next(c for c in actor.findall('./components/component') if c.get('type')=='MotecComponent')
    pages=motec.find('pages')
    main=next(iter(pages.findall('page')),None)
    default=main.find('pagedefault') if main is not None else None
    palette=default.get('paletteBindingId') if default is not None else None
    node=scene=None
    for path in sorted(actor_file.parent.parent.glob('*.i3d')):
        if any(t in path.stem.lower() for t in ('_col','_lod')):continue
        candidate=imp.scene(path)
        if palette in candidate['nodes']:
            scene=candidate;node=scene['nodes'][palette][0][0];break
    if node is None:raise ValueError('Original main-page material could not be found')
    mat=scene['materials'][node.get('materialIds').split()[0]]
    maps={t.get('name',t.tag):scene['files'].get(t.get('fileId')) for t in mat
          if t.tag.endswith('map') or t.tag=='Texture'}
    maps={k:v for k,v in maps.items() if v is not None and v.suffix.lower()=='.dds'}
    widgets=[dict(w.attrib) for p in list(pages.findall('topPage'))+list(pages.findall('page'))[:1] for w in p.findall('.//widget')]
    if 'maskMap1' in maps or 'maskMap2' in maps:
        im=compose(maps,mat,dict(motec.find('default').attrib),widgets,imp.data/'shaders/str4_MotecShader.xml')
    else:
        background=maps.get('backgroundMap') or maps.get('Texture')
        if background is None:raise ValueError('Original background texture could not be found')
        im=Image.open(background).convert('RGBA')
    meta=profile['assets'];expected=meta['background']
    if im.size!=(expected['width'],expected['height']):
        raise ValueError(f'Artwork dimensions changed: installed {im.size}, profile expects {(expected["width"],expected["height"])}')
    out=imp.output/profile['assetDirectory'];out.mkdir(parents=True,exist_ok=True)
    _,actual=fill_atlases(maps,widgets,out,*im.size)
    for gauge in profile.get('gauges',[]) or []:
        id=gauge['id'];asset=meta['gauges'][id]
        if id not in actual or actual[id]!=asset:
            raise ValueError(f'Gauge {id} layout differs from this profile; update its asset mapping')
    crop=meta['crop'];tile=im.crop((crop['x'],crop['y'],crop['x']+crop['width'],crop['y']+crop['height']))
    result=Image.new('RGBA',im.size);result.paste(tile,(0,0))
    save_dds(result,out/expected['file'])
    for field in (profile.get('fields',[]) or [])+(profile.get('auxiliaryFields',[]) or []):
        if field.get('font'):imp.font(field['font'])


def write_installed(project,stage,ready,failures):
    from vehicle_catalog import lua
    assets=project/'assets';assets.mkdir(parents=True,exist_ok=True)
    sources=[]
    if 'Toyota_Supra_GT4' in ready:sources.append('assets/Toyota_Supra_GT4/metadata.lua')
    if 'Ford_Mustang_V8Supercar_2024' in ready:sources.append('assets/Ford_Mustang_V8Supercar_2024/metadata.lua')
    sources.append('assets/fonts/metadata.lua')
    for id in sorted(ready):
        relative=Path(id) if id in ('Toyota_Supra_GT4','Ford_Mustang_V8Supercar_2024') else Path('vehicles')/id
        shutil.copytree(stage/'assets'/relative,assets/relative,dirs_exist_ok=True)
    shutil.copytree(stage/'assets/fonts',assets/'fonts',dirs_exist_ok=True)
    # Publish availability last, so missing optional cars never load stale assets.
    (assets/'installed.lua').write_text('DashboardMod.installedVehicleIds='+lua({id:True for id in sorted(ready)})
        +'\nDashboardMod.installedAssetSources='+lua(sources)+'\n',encoding='utf-8')
    (assets/'setup-report.json').write_text(json.dumps({'installed':sorted(ready),'skipped':failures},indent=2),encoding='utf-8')
    root=project.resolve().as_posix()+'/'
    (project/'local_bootstrap.lua').write_text('-- Generated local entry point; do not commit.\nDashboardMod=DashboardMod or {}\nDashboardMod.root='+lua(root)
        +'\nsource(DashboardMod.root.."script.lua")\n',encoding='utf-8')


def setup(game,project=ROOT,vehicles=None,dlc_export=None):
    from vehicle_catalog import lua
    profiles,entries=definitions(project)
    requested=set(vehicles or profiles)
    unknown=requested-set(profiles)
    if unknown:raise ValueError('Unsupported vehicle IDs: '+', '.join(sorted(unknown)))
    dlc='Ford_Mustang_V8Supercar_2024'
    if dlc in requested and dlc_export:requested.add('Toyota_Supra_GT4')
    actors={}
    for path in (game/'data/vehicles').rglob('*actor.xml'):
        actors[path.relative_to(game/'data/vehicles').parts[0]]=path
    ready=set();failures={}
    scratch=project/'.tools';scratch.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='asset-setup-',dir=scratch) as directory:
        stage=Path(directory);imp=builder(game,stage)
        for id in sorted(requested- {dlc}):
            if id not in actors:failures[id]='Vehicle is not present as loose files in this installation';continue
            try:
                if id=='Toyota_Supra_GT4':
                    subprocess.run([sys.executable,str(project/'tools/prepare_supra.py'),'--game',str(game),'--output',str(stage)],check=True)
                else:build_dashboard(imp,profiles[id],actors[id])
                ready.add(id);print('Prepared '+id,flush=True)
            except (OSError,ValueError,KeyError,StopIteration,ET.ParseError,subprocess.CalledProcessError) as error:
                failures[id]=str(error)
        if dlc in requested:
            if not dlc_export:
                failures[dlc]='Encrypted DLC is not available as loose files. Optional: --dlc-export <folder> containing your mounted-resource exports.'
            elif 'Toyota_Supra_GT4' not in ready:
                failures[dlc]='Shared Supra/DDU10 font assets are unavailable'
            elif not all((dlc_export/name).is_file() for name in ('mustang-background.dds','mustang-mask.dds')):
                failures[dlc]='Export folder must contain mustang-background.dds and mustang-mask.dds'
            else:
                try:
                    subprocess.run([sys.executable,str(project/'tools/prepare_mustang.py'),'--exports',str(dlc_export),'--output',str(stage)],check=True)
                    ready.add(dlc)
                except subprocess.CalledProcessError as error:failures[dlc]='DLC export conversion failed: '+str(error)
        (stage/'assets/fonts').mkdir(parents=True,exist_ok=True)
        (stage/'assets/fonts/metadata.lua').write_text('DashboardMod.fonts='+lua(imp.fonts)+'\n',encoding='utf-8')
        if not ready:raise ValueError('No dashboards were prepared: '+json.dumps(failures))
        write_installed(project,stage,ready,failures)
    print(f'Installed assets for {len(ready)} dashboards. Entry point: {project/"local_bootstrap.lua"}')
    for id,reason in failures.items():print('Skipped '+id+': '+reason)
    return ready,failures


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game',type=Path,help='PMR install directory; otherwise detect Steam libraries or PMR_INSTALL_DIR')
    parser.add_argument('--vehicle',action='append',help='Build only this exact supported ID (repeatable)')
    parser.add_argument('--dlc-export',type=Path,help='Optional folder containing locally exported DLC Mustang textures')
    args=parser.parse_args()
    try:
        game=find_game_install(args.game);print('PMR installation: '+str(game),flush=True)
        setup(game,vehicles=args.vehicle,dlc_export=args.dlc_export.resolve() if args.dlc_export else None)
    except ModuleNotFoundError as error:
        parser.exit(1,f'Missing dependency {error.name}. Run: python -m pip install --target .tools/python -r requirements-dev.txt\n')
    except (OSError,ValueError) as error:parser.exit(1,str(error)+'\n')


if __name__=='__main__':main()
