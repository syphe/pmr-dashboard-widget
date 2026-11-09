"""Prepare the two dashboard textures read through PMR's mounted resource API."""
from pathlib import Path
import io
import shutil
import struct
import sys
import argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image

def save_dds(im,path):
    levels=[]
    while True:
        buffer=io.BytesIO()
        im.save(buffer,format='DDS',pixel_format='DXT5')
        levels.append(buffer.getvalue())
        if im.size==(1,1): break
        im=im.resize((max(1,im.width//2),max(1,im.height//2)),Image.Resampling.LANCZOS)
    header=bytearray(levels[0][:128])
    struct.pack_into('<I',header,8,struct.unpack_from('<I',header,8)[0]|0x20000)
    struct.pack_into('<I',header,28,len(levels))
    struct.pack_into('<I',header,108,0x1000|0x8|0x400000)
    path.write_bytes(header+b''.join(item[128:] for item in levels))

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--vehicle',choices=['Ford_Mustang_V8Supercar_2024','Chevrolet_Camaro_V8Supercar_2024'],default='Ford_Mustang_V8Supercar_2024')
parser.add_argument('--exports',type=Path,default=ROOT/'inspection')
parser.add_argument('--output',type=Path,default=ROOT)
args=parser.parse_args()
camaro=args.vehicle=='Chevrolet_Camaro_V8Supercar_2024'
slug='camaro' if camaro else 'mustang'
asset_key='camaroAssets' if camaro else 'mustangAssets'
texture_prefix='t_chev_camaro' if camaro else 't_ford_mustang'
out=args.output/'assets'/args.vehicle
out.mkdir(parents=True,exist_ok=True)
background=args.exports/f'{slug}-background.dds'
mask=Image.open(args.exports/f'{slug}-mask.dds').convert('RGB')
assert Image.open(background).size==(1024,512) and mask.size==(1024,512)
shutil.copyfile(background,out/'background.dds')
atlas=Image.new('RGBA',(128,64))
entries=[]
for name,box,source_x in [('lights',(76,94,134,132),0),('wiper',(144,94,204,132),64)]:
    x,y,right,bottom=box
    width,height=right-x,bottom-y
    icon=Image.new('RGBA',(width,height),(255,255,255,0))
    alpha=Image.new('L',(width,height))
    alpha.putdata([max(pixel) for pixel in mask.crop(box).get_flattened_data()])
    icon.putalpha(alpha)
    atlas.paste(icon,(source_x,0))
    entries.append(f"  {name}={{file='icons.dds',x={x},y={y},width={width},height={height},sourceX={source_x},sourceY=0,atlasWidth=128,atlasHeight=64}},")
save_dds(atlas,out/'icons.dds')
metadata="""-- Source references recovered from the active car's display material.
DashboardMod.mustangAssets={
 crop={x=0,y=0,width=1024,height=512},
 background={file='background.dds',width=1024,height=512},
 font=DashboardMod.supraAssets.font,
 gauges={},
 icons={
"""+'\n'.join(entries)+"\n }\n}\n"
(out/'metadata.lua').write_text(metadata.replace('mustangAssets',asset_key))
(out/'sources.txt').write_text('Read through the owned, mounted car using PMR copyFile().\n'
    f'Background: dlcS/s1_dlc3/vehicles/{args.vehicle}/Textures/{texture_prefix}_supercar_display1_glow.dds\n'
    f'Mask: dlcS/s1_dlc3/vehicles/{args.vehicle}/Textures/{texture_prefix}_supercar_display_mask1.dds\n'
    'Bindings and digit anchors: live MotecComponent, masterPage + Page1.\n'
    'Font: shared DDU10, prepared with the Supra assets.\n')
print('Prepared',out)
