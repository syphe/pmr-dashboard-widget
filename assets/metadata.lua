-- Bundled runtime metadata. The V8 Supercars share the Supra/DDU10 font.
for _,file in ipairs({
    'assets/Toyota_Supra_GT4/metadata.lua',
    'assets/Ford_Mustang_V8Supercar_2024/metadata.lua',
    'assets/Chevrolet_Camaro_V8Supercar_2024/metadata.lua',
    'assets/fonts/metadata.lua',
}) do
    source(DashboardMod.root..file)
end
