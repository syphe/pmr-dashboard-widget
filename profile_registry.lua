-- Vehicle IDs are directory IDs, never substring matches (GT3/GT4/V8 differ).
local mod=DashboardMod
mod.profiles=mod.profiles or {}
function mod.isAssetBasedProfile(profile)
    return profile.layoutStatus~='analogue-recreation-unverified'
        and profile.layoutStatus~='custom-layout-unverified'
        and not (mod.excludedVehicles and mod.excludedVehicles[profile.id])
end
-- Migrate the two prototype names when loading into an existing debug session.
for i=#mod.profiles,1,-1 do
    local id=mod.profiles[i].id
    if id=='supra' or id=='mustang_v8_evo' or not mod.isAssetBasedProfile(mod.profiles[i]) then table.remove(mod.profiles,i) end
end
function mod.registerProfile(profile)
    if not mod.isAssetBasedProfile(profile) then return false end
    for i,current in ipairs(mod.profiles) do
        if current.id==profile.id then mod.profiles[i]=profile;return end
    end
    mod.profiles[#mod.profiles+1]=profile
end
function mod.vehicleId(actor)
    local c=actor and actor.components
    if not c then return nil end
    local paths={c.AIComp and c.AIComp.xmlFilename or false,
        c.AudioComp and c.AudioComp.actorXmlFileName or false}
    for _,path in ipairs(paths) do
        if type(path)=='string' then
            local id=string.lower(path:gsub('\\','/')):match('/vehicles/([^/]+)/')
                or string.lower(path:gsub('\\','/')):match('^vehicles/([^/]+)/')
            if id then return id end
        end
    end
end
function mod.findProfile(actor)
    local components=actor and actor.components
    for _,path in ipairs({components and components.AIComp and components.AIComp.xmlFilename or false,
        components and components.AudioComp and components.AudioComp.actorXmlFileName or false}) do
        if type(path)=='string' and path:gsub('\\','/'):lower():find('/mods/',1,true) then return nil end
    end
    local id=mod.vehicleId(actor)
    if id then
        for excluded in pairs(mod.excludedVehicles or {}) do
            if string.lower(excluded)==id then return nil end
        end
        for _,profile in ipairs(mod.profiles) do
            if string.lower(profile.id)==id and mod.isAssetBasedProfile(profile) then return profile end
        end
    end
    local c=actor and actor.components
    local root=c and c.car and (c.car.root or c.car.i3dNode)
    if not root or root==0 or type(getName)~='function' then return nil end
    local ok,name=pcall(getName,root)
    if not ok or type(name)~='string' then return nil end
    name=string.lower(name:gsub('\\','/'):match('([^/]+)$') or name)
    for _,profile in ipairs(mod.profiles) do
        if mod.isAssetBasedProfile(profile) then
            for _,alias in ipairs(profile.rootNames or {}) do
                if name==string.lower(alias) then return profile end
            end
        end
    end
end
