-- Development capture from owned, active mounted dashboard scenes only.
-- Loads unlinked meshes without physics or onCreate callbacks, then deletes them.
-- Does not spawn actors, switch cars, alter entitlements or install callbacks.
local base='C:/Users/syphe/source/repos/pmr-dashboard-widget/'
source(base..'inspection/.live-bounds-jobs.lua')
assert(type(getShapeGeometryBoundingSphere)=='function','Bounding-sphere API unavailable')
createFolder(base..'inspection/live-catalog/bounds')
local function numbers(values)
 local out={}
 for i,v in ipairs(values) do out[i]=string.format('%.9g',v) end
 return table.concat(out,' ')
end
local saved=0
for _,job in ipairs(DashboardBoundsJobs) do
 assert(job.active and (job.file:match('^dlcS/') or job.file:match('^dataS/vehicles/')) and not job.file:find('..',1,true))
 local root,reason=loadI3DFile(job.file,false,false,false)
 if root and root~=0 then
  local xml=createXMLFile('dashboardBounds',base..'inspection/live-catalog/bounds/'..job.output,'geometry')
  local ok,err=pcall(function()
   setXMLString(xml,'geometry#source',job.file)
   local index=0
   local function walk(node)
    local key='geometry.node('..index..')';index=index+1
    setXMLString(xml,key..'#name',getName(node))
    setXMLString(xml,key..'#origin',numbers({localToWorld(node,0,0,0)}))
    setXMLString(xml,key..'#axisX',numbers({localDirectionToWorld(node,1,0,0)}))
    setXMLString(xml,key..'#axisY',numbers({localDirectionToWorld(node,0,1,0)}))
    if getHasClassId(node,ClassIds.SHAPE) then
     local x,y,z,r=getShapeGeometryBoundingSphere(node)
     setXMLString(xml,key..'#localSphere',numbers({x,y,z,r}))
     local wx,wy,wz=localToWorld(node,x,y,z)
     setXMLString(xml,key..'#sphereCenter',numbers({wx,wy,wz}))
    end
    for i=0,getNumOfChildren(node)-1 do walk(getChildAt(node,i)) end
   end
   walk(root);saveXMLFile(xml);saved=saved+1
  end)
  delete(xml);delete(root)
  print('DASH_BOUNDS '..job.output..' '..(ok and 'saved' or tostring(err)))
 else print('DASH_BOUNDS failed '..job.file..' reason='..tostring(reason)) end
end
print('DASH_BOUNDS COMPLETE '..saved..'/'..#DashboardBoundsJobs)
