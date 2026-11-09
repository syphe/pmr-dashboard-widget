-- Execute in the installed PMR GIANTS Editor's script console. No game needed.
local file='C:/Program Files (x86)/Steam/steamapps/common/Project Motor Racing/data/vehicles/Toyota_Supra_GT4/Toyota_Supra_GT4_Evo_Display.i3d'
print('[DASH EXPORT] probe',type(io),type(getShapeVertexPositions),type(getShapeVertexTexCoords))
local root,reason=loadI3DFile(file,false,false,true)
print('[DASH EXPORT] root',root,reason)
if root and root~=0 then
    local function walk(node)
        if getName(node)=='TOY_SUP_GT4_EVO_DISPLAY1' then
            local count,positions=getShapeVertexPositions(node)
            local uvCount,uv=getShapeVertexTexCoords(node,0)
            print('[DASH EXPORT] mesh',count,type(positions),uvCount,type(uv))
            if type(positions)=='table' then
                for i=1,math.min(12,#positions) do print('[DASH EXPORT] pos',i,positions[i]) end
            end
            if type(uv)=='table' then
                for i=1,math.min(8,#uv) do print('[DASH EXPORT] uv',i,uv[i]) end
            end
        end
        for i=0,getNumOfChildren(node)-1 do walk(getChildAt(node,i)) end
    end
    walk(root)
    delete(root)
end
print('[DASH EXPORT] probe complete')
