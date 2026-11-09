-- Explicit, bounded capture through PMR's mounted resource APIs.
-- Does not load vehicle actors, change entitlements or install update/draw hooks.
local root=assert(DashboardMod and DashboardMod.root)..'inspection/live-catalog/'
createFolder(DashboardMod.root..'inspection')
createFolder(root)
local function quote(s)
 return '"'..tostring(s):gsub('\\','\\\\'):gsub('"','\\"'):gsub('\r','\\r'):gsub('\n','\\n'):gsub('\t','\\t')..'"'
end
local function json(value)
 local kind=type(value)
 if kind=='string' then return quote(value) end
 if kind=='boolean' or kind=='number' then return tostring(value) end
 if kind~='table' then return 'null' end
 local parts={}
 for k,v in pairs(value) do parts[#parts+1]=quote(k)..':'..json(v) end
 table.sort(parts);return '{'..table.concat(parts,',')..'}'
end
local capture={defs={},files={},vehicles={},root=root}
VehicleAssetCapture=capture
for _,def in pairs(g_VehicleCatalogueManager.defs) do
 local path=(def.ActorFile or ''):gsub('\\','/'):lower()
 if not def.isMod and not def.modName and not path:find('/mods/',1,true) then
  capture.defs[#capture.defs+1]=def
 end
end
table.sort(capture.defs,function(a,b) return a.ID<b.ID end)
local function record(row)
 capture.files[#capture.files+1]=row
 print('VEHICLE_ASSET '..json(row))
end
local function directory(path)
 local parts=path:gsub('\\','/'):match('^(.*)/[^/]+$')
 local current=root:gsub('/$','')
 if parts then
  for part in parts:sub(#root+1):gmatch('[^/]+') do
   current=current..'/'..part;createFolder(current)
  end
 end
end
local function resource(filename,base)
 filename=filename:gsub('\\','/');base=base:gsub('\\','/'):gsub('/$','')
 if filename:lower():sub(1,#base+1)==base:lower()..'/' then return filename end
 local mount,tail=base:match('^([^/]+)/(.*)$')
 if tail and filename:lower():sub(1,#tail+1)==tail:lower()..'/' then return mount..'/'..filename end
 if not filename:find('/',1,true) then return base..'/'..filename end
 return nil
end
function capture.copy(source,destination,kind,id)
 assert(source:match('^[dD][aA][tT][aA][sS]?/') or source:match('^[dD][lL][cC][sS]/'),'Only base-game and DLC resource paths are supported')
 assert(not destination:find('..',1,true) and destination:sub(1,#root)==root,'Unsafe destination')
 directory(destination)
 local ok,result
 if kind=='xml' then
  local handle=loadXMLFile('dashboardCapture',source)
  if handle and handle~=0 then
   ok,result=pcall(saveXMLFileTo,handle,destination);delete(handle)
  else ok=false;result='XML could not be opened' end
 else ok,result=pcall(copyFile,source,destination,true) end
 local exists=fileExists(destination)
 record({vehicle=id,source=source,destination=destination:sub(#root+1),kind=kind,
         success=exists==true,error=not exists and tostring(result) or nil})
 return exists
end
function capture.list(def,folder)
 local context={files={},base=def.vehicleRootPath..folder}
 function context:onFile(name,isDirectory)
  local path=resource(name,self.base)
  if path then self.files[#self.files+1]={source=path,directory=isDirectory==true} end
 end
 local ok,result=pcall(getFiles,def.vehicleRootPath..folder,'onFile',context)
 if not ok then print('VEHICLE_ASSET_LIST '..def.ID..' '..tostring(result)) end
 return context.files
end
function capture.run(first,last,includeInactive)
 for i=first,math.min(last,#capture.defs) do
  local def=capture.defs[i]
  local id=def.vehicleRootPath:gsub('\\','/'):match('([^/]+)$')
  local destination=root..'vehicles/'..id..'/'
  local state={id=id,catalogueId=def.ID,active=def.Active,captureRequested=def.Active or includeInactive==true,scenes=0,textures={}}
  capture.vehicles[def.ID]=state
  if state.captureRequested then
   local actor=def.ActorFile:match('[^/\\]+$');local vdef=def.vdefFile:match('[^/\\]+$')
   capture.copy(def.ActorFile,destination..'data/'..actor,'xml',id)
   capture.copy(def.vdefFile,destination..'data/'..vdef,'xml',id)
   for _,entry in ipairs(capture.list(def,'/')) do
    if not entry.directory and entry.source:lower():match('%.i3d$') then
     state.scenes=state.scenes+1
     capture.copy(entry.source,destination..entry.source:sub(#def.vehicleRootPath+2),'xml',id)
    end
   end
   for _,entry in ipairs(capture.list(def,'/Textures/')) do
    if not entry.directory then state.textures[#state.textures+1]=entry.source end
   end
  end
  print('VEHICLE_ASSET_CAR '..json(state))
 end
 print('VEHICLE_ASSET_BATCH '..first..'-'..last..' total='..#capture.files)
end
print('VEHICLE_ASSET_READY '..#capture.defs)
