-- Shared 2D dashboard renderer and native HUD/editor registration.
local mod = DashboardMod
if mod.release then mod.release() end
mod.revision = (mod.revision or 0) + 1
mod.resources = {}
mod.values = {}
mod.actor = nil
mod.profile = nil
mod.config = mod.config or {width=.32, left=.34, bottom=.018}
mod.widgetId = 'hudDashboard'
local white = {1,1,1,1}
local red = {1,.2,.2,1}
local green = {.3,1,.4,1}

local function finite(v)
    return type(v)=='number' and v==v and math.abs(v)<math.huge
end
mod.isFinite = finite
local function controller(name)
    local gui=g_gui and g_gui.guis and g_gui.guis[name]
    return gui and gui.target
end
function mod.isEditorOpen()
    return g_gui and g_gui.currentGuiName=='MovableWidgetsPage'
end
function mod.release()
    for _,overlay in pairs(mod.resources or {}) do
        if overlay.delete then overlay:delete() end
    end
    mod.resources={}
end
function mod.readNumber(actor, binding)
    if binding.constant~=nil then return binding.constant end
    if not actor then return nil end
    local ok,found,value
    if binding.method then
        local fn=actor[binding.method]
        if type(fn)~='function' then return nil end
        ok,value=pcall(fn,actor)
    elseif binding.param and type(actor.getVehicleParamValue)=='function' then
        ok,found,value=pcall(actor.getVehicleParamValue,actor,binding.param)
        if not found then return nil end
    end
    if not ok then return nil end
    if binding.boolean and type(value)=='boolean' then value=value and 1 or 0 end
    -- Native LapTime stores seconds explicitly; never format the object itself.
    if type(value)=='table' then
        if value.invalid==true and not binding.allowInvalid then return nil end
        value=value.timeSeconds
    end
    if not finite(value) then return nil end
    if binding.absolute then value=math.abs(value) end
    value=value*(binding.scale or 1)+(binding.offset or 0)
    if binding.convert then value=binding.convert(value,actor) end
    if not finite(value) or (binding.min and value<binding.min) then return nil end
    return value
end
function mod.refresh(dt)
    mod.clock=(mod.clock or 0)+(finite(dt) and math.max(0,dt)/1000 or 0)
    local data=g_racingManager and g_racingManager.playerVehicleData
    local actor=data and data.vehicleActor
    local profile=mod.findProfile(actor)
    if actor~=mod.actor or profile~=mod.profile then
        mod.release()
        mod.actor,mod.profile=actor,profile
        mod.values={}
    end
    if not profile then return end
    local values={}
    for _,field in ipairs(profile.fields) do values[field.id]=mod.readNumber(actor,field) end
    for _,gauge in ipairs(profile.gauges) do values['gauge_'..gauge.id]=mod.readNumber(actor,gauge) end
    if values.gauge_rpm==nil then values.gauge_rpm=mod.readNumber(actor,{param='revs'}) end
    for _,indicator in ipairs(profile.indicators or {}) do
        values['indicator_'..indicator.id]=mod.readNumber(actor,{param=indicator.param,boolean=true})
    end
    -- Re-read the live actor, independent of its active Motec page/popups.
    local max,start,shift
    if type(actor.getShiftLightsRange)=='function' then
        local ok
        ok,max,start,shift=pcall(actor.getShiftLightsRange,actor)
        if not ok then max,start,shift=nil,nil,nil end
    end
    values.shiftStart=finite(start) and start or 5600
    values.shiftEnd=finite(shift) and shift or 7350
    values.shiftMax=finite(max) and max or 8000
    values.bestValid=data.bestValidLapTime and data.bestValidLapTime.invalid==false
        and finite(data.bestValidLapTime.timeSeconds) and data.bestValidLapTime.timeSeconds>0
    if not values.bestValid then
        values.delta=nil
        for _,field in ipairs(profile.fields) do
            if field.param=='lapDelta' then values[field.id]=nil end
        end
        for _,gauge in ipairs(profile.gauges) do
            if gauge.param=='lapDelta' then values['gauge_'..gauge.id]=nil end
        end
    end
    mod.values=values
end
function mod.shouldDraw()
    local manager=g_racingManager
    local data=manager and manager.playerVehicleData
    local actor=data and data.vehicleActor
    if g_pendingExit or not manager or manager.active~=true or not actor or actor.active~=true
        or actor.timePaused==true or data.sessionFinished==true or data.mpSessionComplete==true then return false end
    if not PauseManager or type(PauseManager.isPaused)~='function' then return false end
    local ok,paused=pcall(PauseManager.isPaused,PauseManager)
    if not ok or paused~=false then return false end
    local hud=controller('HudOverlay')
    if not hud or type(hud.isHudVisibleReasonSet)~='function'
        or not HudOverlay or type(HudOverlay.HideReasons)~='table' then return false end
    for _,reason in pairs(HudOverlay.HideReasons) do
        local success,hidden=pcall(hud.isHudVisibleReasonSet,hud,reason)
        if not success or hidden~=false then return false end
    end
    return true
end
function mod.format(field,value)
    if field.text then return finite(value) and value>0 and field.text or '' end
    if not finite(value) or (field.positive and value<=0) then return '--' end
    if field.kind=='gear' then
        if value<0 then return 'R' elseif value==0 then return field.zeroNeutral and '0' or 'N' end
        return string.format('%.0f',value)
    elseif field.kind=='time' then
        if value<0 or value>=3600 then return '--' end
        local decimals=field.decimals or 2
        local factor=10^decimals
        local units=math.floor(value*factor+.5)
        return string.format('%d:%0'..(decimals+3)..'.'..decimals..'f',math.floor(units/(60*factor)),units%(60*factor)/factor)
    end
    return string.format(field.format or '%.0f',value)
end
local function getOverlay(profile,file,directory)
    local key=(directory or profile.assetDirectory)..file
    local overlay=mod.resources[key]
    if not overlay then
        overlay=Overlay.new(mod.root..key,0,0,0,0)
        mod.resources[key]=overlay
    end
    return overlay
end
local function uvs(overlay,x,y,w,h,tw,th)
    overlay:setUVs({x/tw,1-(y+h)/th,x/tw,1-y/th,(x+w)/tw,1-(y+h)/th,(x+w)/tw,1-y/th})
end
local function renderImage(overlay,x,y,w,h,color)
    overlay:setPosition(x,y)
    overlay:setDimension(w,h)
    overlay:setColor(unpack(color or white))
    overlay:render()
end
function mod.drawText(profile,bounds,field,text,color)
    local meta=profile.assets or mod.supraAssets
    local font=(field.font and mod.fonts and mod.fonts[field.font]) or meta.font
    if not font then return end
    local overlay=getOverlay(profile,font.file,profile.fontDirectory)
    local height=field.height*(field.heightScale or 1)
    local widthScale=field.widthScale or 1
    local advance=height*.11
    local total=0
    for i=1,#text do
        local glyph=font.glyphs[text:sub(i,i)] or font.glyphs['-']
        total=total+height*glyph.width/glyph.height*widthScale+advance
    end
    total=math.max(0,total-advance)
    local x=field.x+(field.dx or 0)
    if field.align=='right' then x=x-total elseif field.align~='left' then x=x-total/2 end
    local y=field.y+(field.dy or 0)-height/2
    local crop=meta.crop
    if profile.clampText then x=math.max(crop.x,math.min(x,crop.x+crop.width-total)) end
    local sx,sy=bounds.width/profile.width,bounds.height/profile.height
    for i=1,#text do
        local glyph=font.glyphs[text:sub(i,i)] or font.glyphs['-']
        local width=height*glyph.width/glyph.height*widthScale
        uvs(overlay,glyph.x,glyph.y,glyph.width,glyph.height,font.width,font.height)
        renderImage(overlay,bounds.left+(x-crop.x)*sx,
            bounds.bottom+bounds.height-(y-crop.y+profile.topPadding+height)*sy,
            width*sx,height*sy,color)
        x=x+width+advance
    end
end
function mod.drawDashboard(bounds,profile,values)
    profile=profile or mod.profile
    values=values or mod.values
    if not profile then return end
    local meta=profile.assets or mod.supraAssets
    local sx,sy=bounds.width/profile.width,bounds.height/profile.height
    local screenHeight=meta.crop.height*sy
    local background=getOverlay(profile,meta.background.file)
    uvs(background,0,0,meta.crop.width,meta.crop.height,meta.background.width,meta.background.height)
    renderImage(background,bounds.left,bounds.bottom,bounds.width,screenHeight)
    for _,gauge in ipairs(profile.gauges) do
        local value=values['gauge_'..gauge.id]
        local asset=meta.gauges[gauge.id]
        if finite(value) then
            local ratio=math.max(0,math.min(1,(value-gauge.min)/(gauge.max-gauge.min)))
            local frame=math.floor(ratio*(asset.frames-1)+.5)
            local overlay=getOverlay(profile,asset.file)
            uvs(overlay,frame%asset.columns*asset.width,math.floor(frame/asset.columns)*asset.height,
                asset.width,asset.height,asset.atlasWidth,asset.atlasHeight)
            local color=gauge.color or white
            if gauge.high and value>gauge.high then color=gauge.highColor or red end
            if gauge.low and value<gauge.low then color=gauge.lowColor or red end
            renderImage(overlay,bounds.left+(asset.x-meta.crop.x)*sx,
                bounds.bottom+(meta.crop.height-(asset.y-meta.crop.y)-(asset.displayHeight or asset.height))*sy,
                (asset.displayWidth or asset.width)*sx,(asset.displayHeight or asset.height)*sy,color)
        end
    end
    -- Ten main-page delta segments, centred on zero. Missing best lap stays dark.
    local delta=values.delta
    if profile.deltaBar~=false then
      drawFilledRect(bounds.left+(721-meta.crop.x)*sx,
        bounds.bottom+(meta.crop.height-(135-meta.crop.y)-18)*sy,219*sx,18*sy,.03,.04,.05,1)
      for i=1,10 do
        local lit=finite(delta) and ((delta<0 and i<=5 and i>5-math.ceil(math.min(-delta/3,1)*5))
            or (delta>0 and i>5 and i<=5+math.ceil(math.min(delta/3,1)*5)))
        local c=lit and (delta<0 and green or red) or {.06,.07,.08,1}
        drawFilledRect(bounds.left+(728+(i-1)*20.5-meta.crop.x)*sx,
            bounds.bottom+(meta.crop.height-(135-meta.crop.y)-17)*sy,17*sx,17*sy,unpack(c))
      end
    end
    for _,indicator in ipairs(profile.indicators or {}) do
        local value=values['indicator_'..indicator.id]
        local lit=finite(value) and value>(indicator.threshold or 0)
        local color=lit and indicator.onColor or indicator.offColor or {.08,.08,.08,1}
        local asset=meta.icons and meta.icons[indicator.id]
        if asset then
            local overlay=getOverlay(profile,asset.file)
            uvs(overlay,asset.sourceX,asset.sourceY,asset.width,asset.height,asset.atlasWidth,asset.atlasHeight)
            renderImage(overlay,bounds.left+(asset.x-meta.crop.x)*sx,
                bounds.bottom+(meta.crop.height-(asset.y-meta.crop.y)-asset.height)*sy,
                asset.width*sx,asset.height*sy,color)
        else
            drawFilledRect(bounds.left+indicator.x*sx,bounds.bottom+bounds.height-(indicator.y+indicator.height)*sy,
                indicator.width*sx,indicator.height*sy,unpack(color))
        end
    end
    for _,field in ipairs(profile.fields) do
        local value=values[field.id]
        local color=field.color or white
        if finite(value) then
            if field.high and value>field.high then color=field.highColor or red end
            if field.low and value<field.low then color=field.lowColor or red end
            if field.deltaColor then color=value<0 and green or red end
        end
        mod.drawText(profile,bounds,field,mod.format(field,value),color)
    end
    -- The physical shift-light strip sits above the display, within widget bounds.
    local rpm=values.gauge_rpm
    local start,finish=values.shiftStart or 5600,values.shiftEnd or 7350
    local lights=profile.shiftLights
    local count=lights and #lights or 7
    for i=1,count do
        local light=lights and lights[i]
        local threshold=light and light.threshold or start+(light and light.fraction or (i-1)/6)*math.max(1,finish-start)
        local lit=finite(rpm) and rpm>=threshold
        local c=lit and (light and light.color or (i<3 and green or i<5 and {1,.65,.05,1} or red)) or {.08,.09,.1,1}
        if lit and rpm>=(values.shiftMax or 8000) and math.floor((mod.clock or 0)*8)%2==1 then c={.08,.09,.1,1} end
        local x=light and light.x or profile.width/2-139+(i-1)*41
        local y=light and light.y or 13
        local width=light and light.width or 32
        local height=light and light.height or 15
        drawFilledRect(bounds.left+x*sx,
            bounds.bottom+bounds.height-(y+height)*sy,width*sx,height*sy,unpack(c))
    end
end
function mod.bounds(widget)
    local profile=mod.profile or mod.profiles[1]
    local width=mod.config.width
    local height=width*(g_screenAspectRatio or 16/9)*profile.height/profile.width
    local pos=widget and widget.absPosition
    return {left=pos and pos[1] or mod.config.left,bottom=pos and pos[2] or mod.config.bottom,width=width,height=height}
end
local function savedPosition(widget)
    local pos=MovableWidgetsPage and MovableWidgetsPage.loadedPositions and MovableWidgetsPage.loadedPositions[mod.widgetId]
    if pos and finite(pos[1]) and finite(pos[2])
        and (pos[1]~=widget.absPosition[1] or pos[2]~=widget.absPosition[2]) then
        widget:setAbsolutePosition(pos[1],pos[2])
    end
end
local function ensureWidget(target,editor)
    local widget=target[mod.widgetId]
    if not widget then
        widget=GuiElement.new(target)
        widget.id=mod.widgetId
        widget:setAnchor(0,0);widget:setPivot(0,0)
        widget:setAbsolutePosition(mod.config.left,mod.config.bottom)
        target:addElement(widget);target[mod.widgetId]=widget
        savedPosition(widget)
    elseif not widget.dashboardRevision then
        -- Migrate the original full-screen prototype container once.
        widget:setAnchor(0,0);widget:setPivot(0,0)
        widget:setAbsolutePosition(mod.config.left,mod.config.bottom)
        savedPosition(widget)
    end
    local b=mod.bounds(widget)
    if widget.size[1]~=b.width or widget.size[2]~=b.height then widget:setSize(b.width,b.height) end
    if widget.dashboardRevision~=mod.revision then
        widget.dashboardRevision=mod.revision
        widget.handleFocus=false
        widget.frameThickness=widget.frameThickness or {0,0,0,0}
        widget.focusedOffset=widget.focusedOffset or {0,0}
        widget.frameOverlayVisible=widget.frameOverlayVisible or {true,true,true,true}
        widget.update=function(self,dt,...)
            GuiElement.update(self,dt,...)
            if not editor then savedPosition(self) end
            if editor==not not mod.isEditorOpen() then mod.refresh(dt) end
        end
        widget.draw=function(self,...)
            GuiElement.draw(self,...)
            local editing=not not mod.isEditorOpen()
            if editor==editing and mod.profile and (editing or mod.shouldDraw()) then mod.drawDashboard(mod.bounds(self)) end
        end
    end
    if editor then
        local found=false
        for _,entry in ipairs(target.movableWidgets) do if entry==widget then found=true break end end
        if not found then target.movableWidgets[#target.movableWidgets+1]=widget end
        if MovableWidgetsPage.originalPositions and not MovableWidgetsPage.originalPositions[mod.widgetId] then
            MovableWidgetsPage.originalPositions[mod.widgetId]={mod.config.left,mod.config.bottom}
        end
    end
end
function mod.register()
    if not GuiElement or not MovableWidgetsPage then return end
    if mod.placementClass~=MovableWidgetsPage then
        local apply=MovableWidgetsPage.applyWidgetPlacements
        if type(apply)=='function' then
            MovableWidgetsPage.applyWidgetPlacements=function(target,...)
                apply(target,...)
                if target and target[mod.widgetId] then savedPosition(target[mod.widgetId]) end
            end
            mod.placementClass=MovableWidgetsPage
        end
    end
    local hud,editor=controller('HudOverlay'),controller('MovableWidgetsPage')
    if hud then ensureWidget(hud,false) end
    if editor and type(editor.movableWidgets)=='table' then ensureWidget(editor,true) end
end
function mod.install()
    if not mod.installed then
        mod.stockUpdate=update
        mod.installed=true
    end
    update=function(dt,...)
        if mod.stockUpdate then mod.stockUpdate(dt,...) end
        if not g_pendingExit then mod.register() end
    end
    mod.refresh(0)
    mod.register()
    print('[DASHBOARD] Main-page widget loaded: '..tostring(mod.profile and mod.profile.name or 'no supported car'))
end

-- The IDE's "FS Lua: Reload Script in Game" executes this file again.
if mod.installed then mod.install() end
