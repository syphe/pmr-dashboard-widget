-- Bounded verification; both wrappers restore themselves after 60 native calls.
local m=DashboardMod
local editor=g_gui.guis.MovableWidgetsPage.target
local count=0
for _,w in ipairs(editor.movableWidgets) do if w.id==m.widgetId then count=count+1 end end
print('SUPRA_LIVE profile='..tostring(m.profile and m.profile.id)..' font='..m.supraAssets.font.file..' editorEntries='..count)
local refresh,draw=m.refresh,m.drawDashboard
local updates,draws=0,0
m.refresh=function(dt)
    refresh(dt)
    updates=updates+1
    if updates==60 then
        m.refresh=refresh
        print('SUPRA_LIVE updates=60 dt='..tostring(dt)..' rpm='..tostring(m.values.gauge_rpm)..' pressureFL='..tostring(m.values.pressureFL))
    end
end
m.drawDashboard=function(...)
    draw(...)
    draws=draws+1
    if draws==60 then
        m.drawDashboard=draw
        local n=0;for _ in pairs(m.resources) do n=n+1 end
        print('SUPRA_LIVE draws=60 overlays='..n..' gear='..tostring(m.values.gear)..' oil='..tostring(m.values.oil)..' abs='..tostring(m.values.abs))
    end
end
