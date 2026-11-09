-- Check ordinary mounted-directory availability without changing Active flags.
local capture=assert(VehicleAssetCapture,'Run capture-vehicle-assets.lua first')
local count=0
for _,def in ipairs(capture.defs) do
 if not def.Active then
  local files=capture.list(def,'/')
  print('VEHICLE_INACTIVE '..def.ID..' mountedEntries='..#files)
  count=count+1
 end
end
print('VEHICLE_INACTIVE_DONE '..count)
