-- Optional developer startup entry. Normal widget users keep using script.lua.
-- Prepare local jobs first: python tools/runtime_audit.py prepare
local function directory()
 local path
 if debug and type(debug.info)=='function' then path=debug.info(directory,'s')
 elseif debug and type(debug.getinfo)=='function' then path=debug.getinfo(directory,'S').source end
 return type(path)=='string' and path:gsub('^[@=]',''):gsub('\\','/'):match('^(.*[/])inspection/[^/]+$') or nil
end
local root=assert(directory(),'Cannot locate the audit startup folder')
DashboardMod=DashboardMod or {};DashboardMod.root=root
source(root..'script.lua')
source(root..'inspection/runtime-dashboard-audit.lua')
