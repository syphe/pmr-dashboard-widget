-- Bounded, read-only inspection of the owned, mounted Camaro's main page.
local actor=g_racingManager and g_racingManager.playerVehicleData.vehicleActor
local function out(k,v) print('CAMARO '..k..'='..tostring(v)) end
if not actor then out('error','No player actor');return end
local motec
for _,c in pairs(actor.components) do if c.componentType=='MotecComponent' then motec=c end end
if not motec then out('error','No Motec component');return end
local function value(v)
 if type(v)~='table' then return tostring(v) end
 local parts={}
 for k,x in pairs(v) do if type(x)~='table' and type(x)~='function' then parts[#parts+1]=tostring(k)..':'..tostring(x) end end
 table.sort(parts);return '{'..table.concat(parts,',')..'}'
end
out('BEGIN',true)
for _,k in ipairs({'currentPage','activePopup','pageNames','updateParams'}) do
 out('component.'..k,value(motec[k]))
end
local pages={motec.masterPage,motec.pages[1]}
local seen={}
for _,p in ipairs(pages) do
 for k,v in pairs(p) do if k~='widgets' and type(v)~='function' then out(p.name..'.'..k,value(v)) end end
 for name,w in pairs(p.widgets or {}) do
  local label=p.name..'.'..name
  for k,v in pairs(w) do
   if type(v)~='function' and k~='actor' and k~='parentActor' then out(label..'.'..k,value(v)) end
  end
  if w.node and w.node~=0 then
   out(label..'.translation',table.concat({getTranslation(w.node)},','))
   out(label..'.scale',table.concat({getScale(w.node)},','))
   local ok,x,y,z,r=pcall(getShapeGeometryBoundingSphere,w.node)
   if ok then out(label..'.sphere',table.concat({x,y,z,r},',')) end
  end
  local bindings=w.pageSpecificBindings or {}
  local node=bindings[p.name] or bindings[motec.pages[1].name]
  if type(node)=='number' and node~=0 and not seen[node] then
   seen[node]=true
   local ok,count=pcall(getNumOfMaterials,node)
   if ok and count>0 then
    local mat=getMaterial(node,0)
    out('material.node',getName(node));out('material.id',mat)
    for _,map in ipairs({'backgroundMap','maskMap1','maskMap2','rpmAlpha','foregroundMap'}) do
     local success,path=pcall(getMaterialCustomMapFilename,mat,map)
     if success then out('material.'..map,path) end
    end
    CAMARO_INSPECTION={node=node,material=mat}
   end
  end
 end
end
for _,param in ipairs({'gear','revs','speed','engine_temp','oil_temp','water_temp','oil_pressure','brakebias','lap','pos','map','fuel','lapDelta','bestLap'}) do
 local ok,found,v=pcall(actor.getVehicleParamValue,actor,param)
 out('value.'..param,tostring(ok)..','..tostring(found)..','..value(v))
end
out('END',true)
