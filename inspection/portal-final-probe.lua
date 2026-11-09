-- Diagnostic only: one native update, scene-root signature, image-overlay control.
-- This did NOT create a camera overlay in the tested PMR build. See MOTEC_FINDINGS.md.
-- No draw hook; owns and deletes only its cloned subtree and temporary overlays.
local a=g_racingManager.playerVehicleData.vehicleActor
local original=getParent(getParent(a.components.motec.pages[1].pageNode))
local root=clone(original,false,false,false)
link(getRootNode(),root);setVisibility(root,false)
local camera=getChild(root,'Display Cam')
local stockUpdate=update
local p={stockUpdate=stockUpdate,stockDraw=draw,root=root}
MotecPortalProbe=p
function p.stop()
    update=stockUpdate
    if entityExists(root) then delete(root) end
    print('FINAL stopped')
end
update=function(...)
    update=stockUpdate
    stockUpdate(...)
    print('FINAL rendererReady='..tostring(g_rendererReady)..' isRendererReady='..tostring(isRendererReady()))
    local image=createImageOverlay('dataS/menu/base/graph_pixel.png')
    print('FINAL imageControl='..tostring(image))
    if image and image~=0 then delete(image) end
    local function test(label,scene,cam,alpha)
        local id=createRenderOverlay(scene,cam,1.8,512,256,alpha,255,67108864,false,0,false,0,false,0)
        print('FINAL '..label..'='..tostring(id))
        if id and id~=0 then delete(id) end
    end
    test('clonedHidden',root,camera,true)
    setVisibility(root,true)
    test('clonedVisible',root,camera,false)
    setVisibility(root,false)
    test('worldRoot',getRootNode(),getChild(original,'Display Cam'),true)
    p.stop()
    print('FINAL completed')
end
print('FINAL armed')
