-- Read the mounted car's Motec metadata through the game's public Lua objects.
local data=g_racingManager and g_racingManager.playerVehicleData
local actor=data and data.vehicleActor
local function out(label,value) print('MUSTANG '..label..'='..tostring(value)) end
local function scalar(label,value)
    if type(value)=='table' then
        local parts={}
        for i=1,math.min(#value,8) do parts[#parts+1]=tostring(value[i]) end
        if #parts>0 then out(label,table.concat(parts,',')) end
    elseif type(value)~='function' and value~=nil then out(label,value) end
end
out('BEGIN',actor)
if not actor then return end
for name,c in pairs(actor.components or {}) do
    out('component.'..name,c.componentType)
    for _,key in ipairs({'root','i3dNode','actorXmlFileName','xmlFilename'}) do
        if c[key]~=nil then out('component.'..name..'.'..key,c[key]) end
    end
    if c.root then out('component.'..name..'.rootName',getName(c.root)) end
    if c.componentType=='MotecComponent' then
        out('motec.currentPage',c.currentPage)
        out('motec.activePopup',c.activePopup)
        local pages={c.masterPage}
        for _,p in ipairs(c.pages or {}) do pages[#pages+1]=p end
        for _,p in ipairs(pages) do
            out('page',p.name)
            out('pageNode',p.pageNode)
            if p.pageNode and p.pageNode~=0 then out('pageNodeName',getName(p.pageNode)) end
            out('palette',p.defaultPaletteBindingId)
            -- Main and always-on widgets only, bounded to 60 each.
            if p==c.masterPage or p==(c.pages or {})[1] then
                local n=0
                for name,w in pairs(p.widgets or {}) do
                    n=n+1;if n>60 then break end
                    local label=p.name..'.'..name
                    for _,key in ipairs({'type','node','nodeName','fontName','vehicleParam','numChars','align','precision','previousText','updateText','colour','updateColour','highColour','lowColour','minValue','maxValue','highThreshold','lowThreshold','shaderParameter','greenThreshold','amberThreshold','redThreshold','greenT','amberT','redT','pageSpecificBindings'}) do
                        if key=='pageSpecificBindings' and type(w[key])=='table' then
                            for page,node in pairs(w[key]) do out(label..'.binding.'..page,node) end
                        else scalar(label..'.'..key,w[key]) end
                    end
                    if w.node and w.node~=0 then
                        scalar(label..'.translation',{getTranslation(w.node)})
                        scalar(label..'.scale',{getScale(w.node)})
                    end
                end
            end
        end
    end
end
out('END',true)
