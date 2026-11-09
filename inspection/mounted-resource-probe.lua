-- Bounded checks of resource access; writes only under the capture directory.
local root=DashboardMod.root..'inspection/live-catalog/'
local def=g_VehicleCatalogueManager.defs.ID_Chevrolet_Camaro_V8Supercar_2024
local function out(k,v) print('MOUNTED_PROBE '..k..'='..tostring(v)) end
out('BEGIN',true)
for label,path in pairs({actor=def.ActorFile,vdef=def.vdefFile}) do
 local destination=root..'probe-camaro-'..label..'.xml'
 local ok,result=pcall(copyFile,path,destination,true)
 out(label..'.copy',tostring(ok)..','..tostring(result)..','..tostring(fileExists(destination)))
 local xml=loadXMLFile('dashboardResourceProbe',path)
 out(label..'.xml',xml)
 if xml and xml~=0 then
  out(label..'.root',getXMLRootName(xml))
  local saved,value=pcall(saveXMLFileTo,xml,root..'probe-camaro-'..label..'-saved.xml')
  out(label..'.saved',tostring(saved)..','..tostring(value))
  delete(xml)
 end
end
local context={count=0}
function context:onFile(name,isDirectory)
 self.count=self.count+1
 if self.count<=30 then out('file',tostring(name)..','..tostring(isDirectory)) end
end
local ok,result=pcall(getFiles,def.vehicleRootPath..'/Textures/','onFile',context)
out('getFiles',tostring(ok)..','..tostring(result)..',count='..context.count)
out('END',true)
