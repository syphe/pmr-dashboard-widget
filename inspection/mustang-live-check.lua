local m=DashboardMod
if MUSTANG_INSPECTION and MUSTANG_INSPECTION.overlay then
    MUSTANG_INSPECTION.overlay:delete()
    MUSTANG_INSPECTION.overlay=nil
end
local editor=g_gui.guis.MovableWidgetsPage.target
local entries=0
for _,w in ipairs(editor.movableWidgets) do if w.id==m.widgetId then entries=entries+1 end end
print('MUSTANG_LIVE profile='..tostring(m.profile and m.profile.id)..' editorEntries='..entries)
print('MUSTANG_LIVE initial map='..tostring(m.values.map)..' engineTemp='..tostring(m.values.engineTemp)..' brakeBias='..tostring(m.values.brakeBias)..' race='..tostring(m.values.race))
local refresh,draw=m.refresh,m.drawDashboard
local updates,draws=0,0
m.refresh=function(dt)
    refresh(dt);updates=updates+1
    if updates==60 then
        m.refresh=refresh
        print('MUSTANG_LIVE updates=60 dt='..tostring(dt)..' rpm='..tostring(m.values.gauge_rpm)..' map='..tostring(m.values.map)..' engineTemp='..tostring(m.values.engineTemp))
    end
end
m.drawDashboard=function(...)
    draw(...);draws=draws+1
    if draws==60 then
        m.drawDashboard=draw
        local n=0;for _ in pairs(m.resources) do n=n+1 end
        print('MUSTANG_LIVE draws=60 overlays='..n..' gear='..tostring(m.values.gear)..' position='..tostring(m.values.position)..' lap='..tostring(m.values.lap))
    end
end
