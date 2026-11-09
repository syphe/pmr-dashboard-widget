-- Read-only, bounded inventory. Run through the connected Debug Console:
-- source('C:/Users/syphe/source/repos/pmr-dashboard-widget/inspection/motec-probe.lua')
-- source() caches files; use the IDE's script reload after editing this file.
local function dump(label, object)
    if type(object) ~= 'table' then
        print('MOTEC '..label..'='..tostring(object))
        return
    end
    local keys = {}
    for key in pairs(object) do keys[#keys + 1] = key end
    table.sort(keys, function(a, b) return tostring(a) < tostring(b) end)
    for i = 1, math.min(#keys, 80) do
        local key = keys[i]
        print('MOTEC '..label..'.'..tostring(key)..'='..tostring(object[key]))
    end
end

print('MOTEC INVENTORY_BEGIN')
local data = g_racingManager and g_racingManager.playerVehicleData
local actor = data and data.vehicleActor
if actor then
    for name, component in pairs(actor.components or {}) do
        if component.componentType == 'MotecComponent' then
            local label = 'component.'..tostring(name)
            dump(label, component)
            dump(label..'.masterPage', component.masterPage)
            dump(label..'.pages', component.pages)
            dump(label..'.popups', component.popups)
            for i, page in pairs(component.pages or {}) do
                dump(label..'.page.'..tostring(i), page)
            end
            local master = component.masterPage
            local count = 0
            for widgetName, widget in pairs(master and master.widgets or {}) do
                count = count + 1
                if count > 40 then break end
                dump(label..'.widget.'..tostring(widgetName), widget)
            end
        end
    end
else
    print('MOTEC no player actor')
end
print('MOTEC INVENTORY_END')
