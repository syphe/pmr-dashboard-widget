-- Bounded verification, restoring both renderer callbacks after 60 calls.
local m=DashboardMod
if not m or not m.profile or m.profile.id~='Chevrolet_Camaro_V8Supercar_2024' then
 print('CAMARO_LIVE Camaro profile is not selected');return
end
if CAMARO_LIVE_CHECK and CAMARO_LIVE_CHECK.stop then CAMARO_LIVE_CHECK.stop() end
local refresh,draw=m.refresh,m.drawDashboard
local updates,draws=0,0
local probe={}
CAMARO_LIVE_CHECK=probe
function probe.stop()
 if m.refresh==probe.refresh then m.refresh=refresh end
 if m.drawDashboard==probe.draw then m.drawDashboard=draw end
end
probe.refresh=function(dt)
 refresh(dt);updates=updates+1
 if updates==60 then
  m.refresh=refresh
  print('CAMARO_LIVE updates=60 rpm='..tostring(m.values.gauge_rpm)..' temp='..tostring(m.values.engineTemp)..' map='..tostring(m.values.map))
 end
end
probe.draw=function(...)
 draw(...);draws=draws+1
 if draws==60 then
  m.drawDashboard=draw
  local count=0;for _,overlay in pairs(m.resources) do count=count+1 end
  print('CAMARO_LIVE draws=60 overlays='..count..' gear='..tostring(m.values.gear)..' position='..tostring(m.values.position)..' lap='..tostring(m.values.lap))
 end
end
m.refresh,m.drawDashboard=probe.refresh,probe.draw
print('CAMARO_LIVE armed visible='..tostring(m.shouldDraw()))
