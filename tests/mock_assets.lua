-- Metadata-only drawing fixtures. No game textures or installation are needed.
local glyphs={}
for i=32,126 do glyphs[string.char(i)]={x=0,y=0,width=8,height=16} end
DashboardMod.supraAssets={crop={x=84,y=41,width=862,height=471},
 background={file='background.dds',width=1024,height=512},gauges={},
 font={file='font.dds',width=16,height=16,glyphs=glyphs}}
DashboardMod.mustangAssets={crop={x=0,y=0,width=1024,height=512},
 background={file='background.dds',width=1024,height=512},gauges={},
 font=DashboardMod.supraAssets.font,icons={
 lights={file='icons.dds',x=76,y=94,width=58,height=38,sourceX=0,sourceY=0,atlasWidth=128,atlasHeight=64},
 wiper={file='icons.dds',x=144,y=94,width=60,height=38,sourceX=64,sourceY=0,atlasWidth=128,atlasHeight=64}}}
DashboardMod.camaroAssets=DashboardMod.mustangAssets
