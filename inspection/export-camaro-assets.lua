-- Run through PMR's connected Debug Console while driving the owned DLC Camaro.
-- Copy only its two named main-page textures using the mounted resource API.
local root=DashboardMod and DashboardMod.root
if not root then print('CAMARO_EXPORT load script.lua first');return end
local data=g_racingManager and g_racingManager.playerVehicleData
local actor=data and data.vehicleActor
local car=actor and actor.components and actor.components.car
if not car or string.lower(getName(car.root or car.i3dNode))~='chevrolet_camaro_v8supercar_2024.i3d' then
 print('CAMARO_EXPORT current car is not the supported Camaro');return
end
local motec
for _,c in pairs(actor.components) do if c.componentType=='MotecComponent' then motec=c end end
local control=motec and motec.masterPage and motec.masterPage.widgets.dippedBeam
local node=control and control.pageSpecificBindings and control.pageSpecificBindings.Page1
if not node then print('CAMARO_EXPORT main-page material binding is unavailable');return end
local material=getMaterial(node,0)
local prefix='dlcS/s1_dlc3/vehicles/Chevrolet_Camaro_V8Supercar_2024/Textures/'
for _,entry in ipairs({{'backgroundMap','camaro-background.dds'},{'maskMap1','camaro-mask.dds'}}) do
 local resource=getMaterialCustomMapFilename(material,entry[1])
 if type(resource)=='string' and resource:sub(1,#prefix)==prefix then
  resource=resource:gsub('%.png$','.dds')
  local destination=root..'inspection/'..entry[2]
  copyFile(resource,destination,true)
  print('CAMARO_EXPORT '..entry[2]..' exists='..tostring(fileExists(destination)))
 else print('CAMARO_EXPORT unexpected resource for '..entry[1]) end
end
