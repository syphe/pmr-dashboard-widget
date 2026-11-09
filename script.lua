-- Load directly as PMR's startup script; all runtime assets are bundled.
DashboardMod = DashboardMod or {}
local function scriptDirectory()
    -- PMR exposes Luau debug.info; standard Lua tools expose debug.getinfo.
    local path
    if debug and type(debug.info)=='function' then
        path=debug.info(scriptDirectory,'s')
    elseif debug and type(debug.getinfo)=='function' then
        path=debug.getinfo(scriptDirectory,'S').source
    end
    if type(path)~='string' then return nil end
    path=path:gsub('^[@=]',''):gsub('\\','/')
    return path:match('^(.*[/])[^/]+$') or (path=='script.lua' and './' or nil)
end
DashboardMod.root = DashboardMod.root or g_currentModDirectory or scriptDirectory()
assert(type(DashboardMod.root)=='string','Set DashboardMod.root to the folder containing script.lua')
DashboardMod.root=DashboardMod.root:gsub('\\','/'):gsub('/?$','/')
-- Clear availability state left by the former per-install setup workflow.
DashboardMod.installedVehicleIds=nil
DashboardMod.installedAssetSources=nil
source('dataS/s4sGame/scripts/main.lua')

for _,file in ipairs({'profile_registry.lua','catalog/vehicles.lua','assets/metadata.lua'}) do
    source(DashboardMod.root..file)
end
DashboardMod.profiles={}
for _,id in ipairs({'Toyota_Supra_GT4','Ford_Mustang_V8Supercar_2024','Chevrolet_Camaro_V8Supercar_2024'}) do
    source(DashboardMod.root..'profiles/'..id..'.lua')
end
for _,entry in ipairs(DashboardMod.catalog) do
    source(DashboardMod.root..entry.file)
end
source(DashboardMod.root..'dashboard_widget.lua')
DashboardMod.install()
