-- Run in GIANTS Editor 10.5.2: source('<repo>/tools/editor_geometry_export.lua')
-- The game need not be running. Reads local I3Ds; writes only catalog/geometry.
local base='C:/Users/syphe/source/repos/pmr-dashboard-widget/'
source(base..'tools/editor_geometry_jobs.lua')
local function numbers(values)
    local t={}
    for i,v in ipairs(values) do t[i]=string.format('%.9g',v) end
    return table.concat(t,' ')
end
for _,job in ipairs(DashboardGeometryJobs) do
    local root,reason=loadI3DFile(job.file,false,false,true)
    if root and root~=0 then
        local xml=createXMLFile('dashGeometry',base..'catalog/geometry/'..job.output,'geometry')
        setXMLString(xml,'geometry#source',job.file)
        local index=0
        local function walk(node)
            local key='geometry.node('..index..')'
            index=index+1
            setXMLString(xml,key..'#name',getName(node))
            local x,y,z=localToWorld(node,0,0,0)
            setXMLString(xml,key..'#origin',numbers({x,y,z}))
            local xx,xy,xz=localDirectionToWorld(node,1,0,0)
            local yx,yy,yz=localDirectionToWorld(node,0,1,0)
            setXMLString(xml,key..'#axisX',numbers({xx,xy,xz}))
            setXMLString(xml,key..'#axisY',numbers({yx,yy,yz}))
            if getHasClassId(node,ClassIds.SHAPE) then
                local count,positions=getShapeVertexPositions(node)
                if count and count>0 and count<=50000 and type(positions)=='table' then
                    local _,uv=getShapeVertexTexCoords(node,0)
                    local world={}
                    for i=1,#positions,3 do
                        local a,b,c=localToWorld(node,positions[i],positions[i+1],positions[i+2])
                        world[#world+1]=a;world[#world+1]=b;world[#world+1]=c
                    end
                    setXMLInt(xml,key..'#count',count)
                    setXMLString(xml,key..'#positions',numbers(world))
                    if type(uv)=='table' then setXMLString(xml,key..'#uv',numbers(uv)) end
                end
            end
            for i=0,getNumOfChildren(node)-1 do walk(getChildAt(node,i)) end
        end
        walk(root)
        saveXMLFile(xml);delete(xml);delete(root)
        print('[DASH EXPORT] saved '..job.output..' ('..index..' nodes)')
    else
        print('[DASH EXPORT] failed '..job.file..' reason '..tostring(reason))
    end
end
print('[DASH EXPORT] all geometry exports complete')
