-- Recovered from the active DLC Camaro's MotecComponent on 10 November 2026.
-- Main-page geometry/bindings and texture hashes match the Mustang capture.
-- Main page only. Texture positions are pixels, top-left origin.
local profile={
    id='Chevrolet_Camaro_V8Supercar_2024',name='AUS V8 Evo Camaro',
    rootNames={'Chevrolet_Camaro_V8Supercar_2024.i3d'},layoutStatus='hand-tuned',
    width=1024,height=552,topPadding=40,assetDirectory='assets/Chevrolet_Camaro_V8Supercar_2024/',
    fontDirectory='assets/Toyota_Supra_GT4/',assets=DashboardMod.camaroAssets,deltaBar=false,
    fields={
        {id='gear',param='gear',x=510,y=246,height=220,kind='gear'},
        {id='best',param='bestLap',x=850,y=123,height=60,kind='time',decimals=1,positive=true},
        {id='delta',param='lapDelta',x=850,y=229,height=60,format='%+.2f',deltaColor=true},
        {id='position',param='pos',x=181,y=226,height=70,format='%.0f'},
        {id='lap',param='lap',x=328,y=226,height=70,format='%.0f'},
        {id='engineTemp',param='engine_temp',x=175,y=458,height=66,format='%.0f',high=115},
        {id='brakeBias',param='brakebias',x=512,y=458,height=66,format='%.1f'},
        {id='map',param='map',x=838,y=458,height=66,format='%.0f'},
        {id='race',param='israce',boolean=true,text='RACE',x=30,y=26,height=26,align='left',color={.9,.6,.05,1}},
        {id='qualifying',param='isqualifying',boolean=true,text='QUALIFY',x=30,y=26,height=26,align='left',color={.9,.05,.05,1}},
        {id='practice',param='ispractice',boolean=true,text='PRACTICE',x=30,y=26,height=26,align='left',color={.15,.3,1,1}},
    },
    gauges={},
    shiftLights={
        {x=380,y=12,width=52,height=18,threshold=6000,color={.1,1,.15,1}},
        {x=450,y=12,width=52,height=18,threshold=6450,color={.1,1,.15,1}},
        {x=520,y=12,width=52,height=18,threshold=6900,color={.1,1,.15,1}},
        {x=590,y=12,width=52,height=18,threshold=7350,color={1,.05,.05,1}},
    },
    indicators={
        {id='lights',param='lights',onColor={.65,.8,1,1},offColor={.08,.09,.1,1}},
        {id='wiper',param='wiper',onColor={.65,.8,1,1},offColor={.08,.09,.1,1}},
        {id='frontLocked',param='frontLocked',x=210,y=12,width=52,height=18,onColor={.9,.3,.3,1}},
        {id='rearLocked',param='rearLocked',x=762,y=12,width=52,height=18,onColor={.9,.7,0,1}},
    },
}
DashboardMod.profiles=DashboardMod.profiles or {}
for i,existing in ipairs(DashboardMod.profiles) do
    if existing.id==profile.id then DashboardMod.profiles[i]=profile return end
end
DashboardMod.profiles[#DashboardMod.profiles+1]=profile
