local module_name = 'hudDashboard'

source('dataS/s4sGame/scripts/main.lua')

DashboardWidget = {}
function DashboardWidget:new(o, hudOverlay)
    o = o or {}
    setmetatable(o, self)
    self.__index = self

    self.widget = GuiElement.new(hudOverlay.target)
    self.widget.id = module_name

    -- Update seems to run every cycle
    self.widget.update = function(self, dt, ...)
        GuiElement.update(self, dt, ...)

        print('update widget ')
    end

    -- Draw only draws seemingly every frame
    self.widget.draw = function(self, ...)
        GuiElement.draw(self, ...)

        print('draw widget ')

        drawFilledRect(10, 10, 1000, 1000, 0, 0, 0, 1.0) -- Draw a red rectangle
    end

    if hudOverlay.target[self.widget.id] then
        hudOverlay.target:removeElement(hudOverlay.target[self.widget.id])
    end

    hudOverlay.target:addElement(self.widget)
    hudOverlay.target[self.widget.id] = self.widget

    return o
end

-- Store the original init and update functions before we override them below
local _init = init
local _update = update
local _draw = draw

function init(...)
        _init(...)
--     print(module_name .. ' init')
--     local widget = DashboardWidget:new()
--     print("Initialized widget:", widget)
        print(module_name .. ' init')
end

local dashboardWidgetInstance = nil

function update(...)
        _update(...)

        local hudOverlay = g_gui.guis.HudOverlay
        if hudOverlay and not dashboardWidgetInstance then
            dashboardWidgetInstance = DashboardWidget:new({}, hudOverlay)
            print("Created dashboardWidgetInstance:", dashboardWidgetInstance)
        elseif not hudOverlay and dashboardWidgetInstance then
            dashboardWidgetInstance = nil
            print("Removed dashboardWidgetInstance")
        end
end

function draw(...)
        _draw(...)
end

function createWidget()
        local hudOverlay = g_gui.guis.HudOverlay
        if not hudOverlay then 
            print("HudOverlay not found, cannot create widget.")
            return nil
        end
    local widget = DashboardWidget:new({}, hudOverlay)
    print("Created widget:", widget)
    return widget
end

function report()
end

print(module_name .. ' loaded')
