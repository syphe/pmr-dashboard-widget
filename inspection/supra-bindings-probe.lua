local a=g_racingManager and g_racingManager.playerVehicleData and g_racingManager.playerVehicleData.vehicleActor
print('SUPRA_BIND actor='..tostring(a))
if not a then return end
local car=a.components and a.components.car
if car and car.root then print('SUPRA_BIND root='..getName(car.root)) end
for _,name in ipairs({'revs','speed','gear','fuel','oil_temp','water_temp','brakebias','lapTime','bestLap','predictedLap','lapDelta','fuelDelta','previousFuelDelta','tcs','abs','wheel1.tyre_pressure'}) do
    local ok,found,value=pcall(a.getVehicleParamValue,a,name)
    print('SUPRA_BIND '..name..' ok='..tostring(ok)..' found='..tostring(found)..' value='..tostring(value))
end
for _,c in pairs(a.components or {}) do
    if c.componentType=='MotecComponent' then
        for _,page in pairs(c.pages or {}) do
            if page.name=='Page1' then
                for name,w in pairs(page.widgets or {}) do
                    print('SUPRA_BIND widget='..name..' text='..tostring(w.updateText)..' param='..tostring(w.vehicleParam))
                end
            end
        end
    end
end
