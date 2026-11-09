"""Overlay-ready BC3 DDS with a full mip chain."""
import io
import struct
from PIL import Image


def save_dds(im,path):
    levels=[]
    while True:
        buffer=io.BytesIO();im.convert('RGBA').save(buffer,format='DDS',pixel_format='DXT5')
        levels.append(buffer.getvalue())
        if im.size==(1,1):break
        im=im.resize((max(1,im.width//2),max(1,im.height//2)),Image.Resampling.LANCZOS)
    header=bytearray(levels[0][:128])
    struct.pack_into('<I',header,8,struct.unpack_from('<I',header,8)[0]|0x20000)
    struct.pack_into('<I',header,28,len(levels));struct.pack_into('<I',header,108,0x1000|0x8|0x400000)
    path.write_bytes(header+b''.join(level[128:] for level in levels))
