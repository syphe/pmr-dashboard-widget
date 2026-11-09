-- Original 1024 x 512 texture coordinates, top-left origin. Only Page1 is used.
-- Each field supports dx/dy, height, widthScale, scale/offset and format/convert.
-- The shared renderer handles placement and unit conversion; add future cars here.
local profile = {
        id='supra', name='Toyota GR Supra GT4 Evo', rootPattern='toyota_supra',
        width=862, height=511, topPadding=40, assetDirectory='assets/supra/',
        fields={
            {id='fuelPrevious', param='previousFuelDelta', x=195,y=116,height=24,format='%.2fL',min=0},
            {id='fuelUsed', param='fuelDelta', x=195,y=173,height=14,format='%.2fL',min=0},
            {id='brakeBias', param='brakebias', x=195,y=204,height=24,format='%.1f',color={.2,.6,1,1}},
            {id='best', param='bestLap', x=404,y=107,height=15,kind='time',positive=true},
            {id='actual', param='lapTime', x=515,y=107,height=15,kind='time',allowInvalid=true},
            {id='predicted', param='predictedLap', x=638,y=107,height=15,kind='time',positive=true},
            {id='delta', param='lapDelta', x=830,y=199,height=28,format='%+.2f',deltaColor=true},
            {id='gear', param='gear', x=515,y=263,height=96,kind='gear'},
            {id='speed', method='getForwardSpeedKPH', x=515,y=440,height=56,format='%.0f',absolute=true},
            {id='fuel', param='fuel', x=515,y=402,height=28,format='%.0fL',low=10},
            {id='oil', param='oil_temp', x=230,y=337,height=29,format='%.0f!C',high=150},
            {id='water', param='water_temp', x=800,y=337,height=29,format='%.0f!C',high=115},
            {id='pressureFL',param='wheel1.tyre_pressure',x=199,y=420,height=25,align='right',scale=.00001,format='%.2f'},
            {id='pressureFR',param='wheel2.tyre_pressure',x=260,y=420,height=25,align='left',scale=.00001,format='%.2f'},
            {id='pressureRL',param='wheel3.tyre_pressure',x=199,y=456,height=25,align='right',scale=.00001,format='%.2f'},
            {id='pressureRR',param='wheel4.tyre_pressure',x=260,y=456,height=25,align='left',scale=.00001,format='%.2f'},
            -- The original actor XML explicitly fixes these two labels at zero.
            {id='powerSteering',constant=0,x=759,y=411,height=28,format='%.0f'},
            {id='throttleLabel',constant=0,x=854,y=411,height=28,format='%.0f'},
            {id='tc',param='tcs',x=759,y=479,height=28,format='%.0f'},
            {id='abs',param='abs',x=854,y=479,height=28,format='%.0f'},
        },
        gauges={
            {id='rpm',param='revs',min=0,max=8000,high=6600,color={1,1,1,1},highColor={1,.05,.05,1}},
            {id='oil',param='oil_temp',min=60,max=160,high=150,color={.6,1,.6,1}},
            {id='water',param='water_temp',min=60,max=100,high=115,color={.6,1,.6,1}},
            {id='fuel',param='fuel',min=0,max=120,low=10,color={.6,1,.6,1}},
        },
}
DashboardMod.profiles=DashboardMod.profiles or {}
for i,existing in ipairs(DashboardMod.profiles) do
    if existing.id==profile.id then DashboardMod.profiles[i]=profile return end
end
DashboardMod.profiles[#DashboardMod.profiles+1]=profile
