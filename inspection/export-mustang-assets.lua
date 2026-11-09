-- Run once in PMR's connected Debug Console while in the DLC Mustang.
-- Reads two named textures through the normal mounted resource API.
local root=DashboardMod and DashboardMod.root
if not root then print('MUSTANG_EXPORT load local_bootstrap.lua first');return end
local data=g_racingManager and g_racingManager.playerVehicleData
local actor=data and data.vehicleActor
local car=actor and actor.components and actor.components.car
if not car or not string.find(string.lower(getName(car.root or car.i3dNode)),'ford_mustang_v8supercar_2024',1,true) then
    print('MUSTANG_EXPORT current car is not the supported Mustang');return
end
local motec
for _,c in pairs(actor.components) do if c.componentType=='MotecComponent' then motec=c end end
local control=motec and motec.masterPage and motec.masterPage.widgets.dippedBeam
local node=control and control.pageSpecificBindings and control.pageSpecificBindings.Page1
if not node then print('MUSTANG_EXPORT main-page material binding is unavailable');return end
local material=getMaterial(node,0)
local prefix='dlcS/s1_dlc3/vehicles/Ford_Mustang_V8Supercar_2024/Textures/'
for _,entry in ipairs({{'backgroundMap','mustang-background.dds'},{'maskMap1','mustang-mask.dds'}}) do
    local resource=getMaterialCustomMapFilename(material,entry[1])
    if type(resource)=='string' and resource:sub(1,#prefix)==prefix then
        resource=resource:gsub('%.png$','.dds')
        local destination=root..'inspection/'..entry[2]
        copyFile(resource,destination,true)
        print('MUSTANG_EXPORT '..entry[2]..' exists='..tostring(fileExists(destination)))
    else
        print('MUSTANG_EXPORT unexpected resource for '..entry[1])
    end
end
