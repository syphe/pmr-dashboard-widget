-- Local development entry point. Load this file through the GIANTS debugger.
DashboardMod = DashboardMod or {}
DashboardMod.root = DashboardMod.root or 'C:/Users/syphe/source/repos/pmr-dashboard-widget/'
source('dataS/s4sGame/scripts/main.lua')

for _,file in ipairs({'assets/supra/metadata.lua','assets/mustang/metadata.lua','profiles/supra.lua','profiles/mustang.lua','dashboard_widget.lua'}) do
    source(DashboardMod.root..file)
end
DashboardMod.install()
