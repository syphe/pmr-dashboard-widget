-- Snapshot base-game and DLC definitions without calling catalogue mutators.
local function isModData(v)
 if type(v)~='table' then return false end
 if v.isMod or v.modName then return true end
 for _,value in pairs(v) do
  if type(value)=='string' and value:gsub('\\','/'):lower():find('/mods/',1,true) then return true end
 end
 return false
end
local function quote(s)
 return '"'..tostring(s):gsub('\\','\\\\'):gsub('"','\\"'):gsub('\r','\\r'):gsub('\n','\\n'):gsub('\t','\\t')..'"'
end
local function json(v,depth,seen)
 local kind=type(v)
 if kind=='string' then return quote(v)
 elseif kind=='number' or kind=='boolean' then return tostring(v)
 elseif kind~='table' then return 'null' end
 if depth<=0 or seen[v] then return 'null' end
 seen[v]=true
 local keys={};for k,value in pairs(v) do
  if type(k)=='string' and type(value)~='function' and type(value)~='userdata' and not isModData(value) then keys[#keys+1]=k end
 end
 table.sort(keys)
 local parts={}
 for _,k in ipairs(keys) do parts[#parts+1]=quote(k)..':'..json(v[k],depth-1,seen) end
 -- Preserve numeric-keyed lists/maps as JSON objects with string keys.
 for k,value in pairs(v) do
  if type(k)=='number' and type(value)~='function' and type(value)~='userdata' and not isModData(value) then
   parts[#parts+1]=quote(k)..':'..json(value,depth-1,seen)
  end
 end
 seen[v]=nil;return '{'..table.concat(parts,',')..'}'
end
local m=g_VehicleCatalogueManager
if not m or not m.defs then print('VEHICLE_CAPTURE error=no catalogue');return end
local count=0
local classes={}
print('VEHICLE_CAPTURE BEGIN')
for k,v in pairs(m.defs) do
 if not isModData(v) then
  count=count+1
  classes[v.VehicleClass]=m.vehicleClassDef[v.VehicleClass]
  print('VEHICLE_CAPTURE DEF '..json({key=tostring(k),definition=v},5,{}))
 end
end
print('VEHICLE_CAPTURE CLASSES '..json(classes,4,{}))
print('VEHICLE_CAPTURE END count='..count)
