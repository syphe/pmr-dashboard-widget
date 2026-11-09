"""Convert installed PMR Supra Page1 assets to cached 2D overlays (local use)."""
from pathlib import Path
import math
import io
import struct
import sys
import xml.etree.ElementTree as ET
import argparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.tools/python'))
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--game',type=Path,default=Path(r'C:\Program Files (x86)\Steam\steamapps\common\Project Motor Racing'))
parser.add_argument('--output',type=Path,default=ROOT)
args=parser.parse_args()
DATA = args.game / 'data'
OUT = args.output / 'assets/Toyota_Supra_GT4'
OUT.mkdir(parents=True, exist_ok=True)
TEX = DATA / 'vehicles/Toyota_Supra_GT4/Textures'

def save_dds(im, path):
    """BC3 texture with a complete offline-generated mip chain."""
    levels=[]
    while True:
        buffer=io.BytesIO()
        im.convert('RGBA').save(buffer,format='DDS',pixel_format='DXT5')
        levels.append(buffer.getvalue())
        if im.size==(1,1): break
        im=im.resize((max(1,im.width//2),max(1,im.height//2)),Image.Resampling.LANCZOS)
    header=bytearray(levels[0][:128])
    struct.pack_into('<I',header,8,struct.unpack_from('<I',header,8)[0] | 0x20000)
    struct.pack_into('<I',header,28,len(levels))
    struct.pack_into('<I',header,108,0x1000 | 0x8 | 0x400000)
    path.write_bytes(header+b''.join(level[128:] for level in levels))

# Preserve the display itself; omit the grey off-screen UV padding.
crop = (84, 41, 946, 512)
background=Image.new('RGBA',(1024,512))
background.paste(Image.open(TEX / 't_toy_sup_gt4_evo_display1_alb.dds').crop(crop),(0,0))
save_dds(background,OUT / 'background.dds')
mask = Image.open(TEX / 't_toy_sup_gt4_evo_display1_layer1_mask.dds').convert('RGB')
pixels = mask.load()
definitions = {
    'rpm': ((374, 140, 659, 377), (0, 0, 3)),
    'oil': ((174, 227, 287, 322), (3, 3, 1)),
    'water': ((744, 227, 858, 322), (0, 3, 1)),
    'fuel': ((457, 364, 576, 386), (2, 3, 3)),
}
metadata = []
for name, (box, key) in definitions.items():
    x0, y0, x1, y1 = box
    w, h = x1-x0, y1-y0
    cols, rows, count = 9, 8, 65
    atlas_w = 2 ** math.ceil(math.log2(w*cols))
    atlas_h = 2 ** math.ceil(math.log2(h*rows))
    atlas = Image.new('RGBA', (atlas_w, atlas_h))
    matches = []
    for y in range(h):
        for x in range(w):
            rgb = pixels[x+x0, y+y0]
            value = max(rgb)/255
            if value < .025:
                continue
            quantized = tuple(round(c/max(rgb)*3) for c in rgb)
            if quantized == key:
                matches.append((x,y,value))
    assert matches, (name, 'mask palette missing')
    for frame in range(count):
        im = Image.new('RGBA', (w,h))
        target = im.load()
        for x,y,value in matches:
            # Invert the source brightness ramp as the Motec shader does.
            alpha = round(max(0,min(1,(value-(1-frame/64))*64))*255)
            target[x,y] = (255,255,255,alpha)
        atlas.paste(im, ((frame%cols)*w, (frame//cols)*h))
    save_dds(atlas,OUT / (name+'.dds'))
    metadata.append(f"    {name} = {{file='{name}.dds', x={x0}, y={y0}, width={w}, height={h}, atlasWidth={atlas_w}, atlasHeight={atlas_h}, columns={cols}, frames={count}}},")

source = Image.open(DATA / 'shared/alphabet/font_ddu10_1.dds').convert('L')
# The sharp atlas omits the degree glyph used by the actor's '!C' format.
# Place a small ring in its otherwise empty cell, retaining the common baseline.
degree_left=round(3*source.width/37)
ImageDraw.Draw(source).ellipse((degree_left+6,69,degree_left+17,81),outline=255,width=3)
font = Image.new('RGBA', source.size, (255,255,255,255))
font.putalpha(source)
save_dds(font,OUT / 'font.dds')
font_node = ET.parse(DATA / 'shared/alphabet/fonts.xml').find("font[@name='DDU10']")
glyphs = []
for char in font_node.findall('character'):
    index = int(char.get('uvIndex'))
    left, right = round((index%37)*source.width/37), round((index%37+1)*source.width/37)
    top = index//37*64
    cell = source.crop((left,top,right,top+64))
    bounds = cell.getbbox()
    if bounds:
        # Keep row height so punctuation/degree symbols retain their baseline.
        x = left+bounds[0]
        width = bounds[2]-bounds[0]
        text = char.get('value').replace('\\','\\\\').replace("'","\\'")
        glyphs.append(f"    ['{text}'] = {{x={x}, y={top}, width={width}, height=64}},")
(OUT / 'metadata.lua').write_text("DashboardMod.supraAssets = {\n crop={x=84,y=41,width=862,height=471},\n background={file='background.dds',width=1024,height=512},\n gauges={\n"+'\n'.join(metadata)+"\n },\n font={file='font.dds',width=2048,height=128,glyphs={\n"+'\n'.join(glyphs)+"\n }}\n}\n")
print('Prepared Supra background, four gauge atlases, font and metadata:',OUT)

