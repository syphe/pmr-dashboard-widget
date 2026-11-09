local a=g_racingManager.playerVehicleData.vehicleActor
local m
for _,c in pairs(a.components) do if c.componentType=='MotecComponent' then m=c end end
local node=m.masterPage.widgets.dippedBeam.pageSpecificBindings.Page1
local function out(k,v) print('MUSTANG_MATERIAL '..k..'='..tostring(v)) end
out('node',node)
out('name',getName(node))
out('materials',getNumOfMaterials(node))
local mat=getMaterial(node,0)
out('material',mat)
out('shader',getMaterialCustomShaderFilename(mat))
for _,name in ipairs({'backgroundMap','backgroundEmissiveMap','maskMap1','maskMap2','rpmAlpha','foregroundMap'}) do
 local ok,path=pcall(getMaterialCustomMapFilename,mat,name)
 out(name,ok and path or 'unavailable')
end
out('boundingSphere',table.concat({getShapeGeometryBoundingSphere(node)},','))
local root=getParent(getParent(m.pages[1].pageNode))
for i=0,math.min(getNumOfChildren(root)-1,14) do local c=getChildAt(root,i);out('child',tostring(c)..' '..getName(c)) end
for _,p in ipairs({'revs','map','engine_temp','brakebias','lap','pos','speed','fuel'}) do
 local ok,found,value=pcall(a.getVehicleParamValue,a,p)
 out('value.'..p,tostring(ok)..' '..tostring(found)..' '..tostring(value))
end
MUSTANG_INSPECTION={backgroundNode=node,material=mat,background=getMaterialCustomMapFilename(mat,'backgroundMap')}
