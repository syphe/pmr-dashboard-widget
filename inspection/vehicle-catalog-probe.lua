-- Read-only bounded discovery of the live vehicle catalogue.
local function out(key,value) print('VEHICLE_PROBE '..key..'='..tostring(value)) end
local manager=g_VehicleCatalogueManager
out('BEGIN',manager)
if not manager then return end
local function summary(label,t,limit)
 local keys={};for k in pairs(t) do keys[#keys+1]=k end
 table.sort(keys,function(a,b) return tostring(a)<tostring(b) end)
 out(label..'.count',#keys)
 for i=1,math.min(#keys,limit) do
  local k=keys[i];local v=t[k]
  if type(v)=='table' then
   local parts={};local count=0
   for a,b in pairs(v) do
    count=count+1
    if type(b)~='table' and type(b)~='function' then parts[#parts+1]=tostring(a)..':'..tostring(b) end
   end
   table.sort(parts);out(label..'.'..tostring(k),'table['..count..'] '..table.concat(parts,';'))
  else out(label..'.'..tostring(k),type(v)..':'..tostring(v)) end
 end
end
local definitions={}
for id,def in pairs(manager.defs or {}) do
 local path=(def.ActorFile or ''):gsub('\\','/'):lower()
 if not def.isMod and not def.modName and not path:find('/mods/',1,true) then definitions[id]=def end
end
summary('definitions',definitions,6)
if VehicleCatalogueManager then summary('class',VehicleCatalogueManager,100) end
out('END',true)
