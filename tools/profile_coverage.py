"""Audit active official vehicles against the portable runtime bundle."""
from pathlib import Path
import json
import struct
from collections import Counter
from preview_catalog import runtime
from profile_evidence import evidence

ROOT=Path(__file__).resolve().parents[1]


def audit():
    engine=runtime();mod=engine.globals().DashboardMod
    profiles={p.id:p for _,p in mod.profiles.items()}
    catalogue=json.loads((ROOT/'catalog/game-vehicles.json').read_text(encoding='utf-8'))
    exclusions=json.loads((ROOT/'catalog/exclusions.json').read_text())
    assert set(profiles)=={p.stem for p in (ROOT/'profiles').glob('*.lua')},'Unregistered profile files'
    assert not set(profiles)&set(exclusions),'Excluded profiles remain enabled'
    assert set(profiles)|set(exclusions)<={r['vehicleId'] for r in catalogue},'Unofficial vehicle in bundle'
    result=[]
    for row in catalogue:
        id=row['vehicleId'];p=profiles.get(id);assets=set()
        if p:
            meta=p.assets or mod.supraAssets
            assets.add(p.assetDirectory+meta.background.file)
            if meta.palette is not None:assets.add(p.assetDirectory+meta.palette.file)
            for _,f in p.fields.items():
                font=mod.fonts[f.font] if f.font else meta.font
                assert font is not None,(id,'missing font',f.font)
                directory=p.fontDirectory if p.fontDirectory is not None else p.assetDirectory
                assets.add(directory+font.file)
            for _,g in (p.gauges or engine.table()).items():assets.add(p.assetDirectory+meta.gauges[g.id].file)
            for _,icon in (meta.icons or engine.table()).items():assets.add(p.assetDirectory+icon.file)
            for name in assets:
                path=(ROOT/name).resolve()
                assert path.is_relative_to(ROOT) and path.is_file(),(id,'Missing asset',name)
                with path.open('rb') as source:header=source.read(128)
                assert header[:4]==b'DDS ' and len(header)==128,(id,'Invalid DDS',name)
                h,w=struct.unpack_from('<II',header,12)
                assert w>0 and h>0 and path.stat().st_size>128,(id,'Empty DDS',name)
            status='profile'
        elif id in exclusions:
            assert 'nalogue' in exclusions[id],(id,'Non-analogue exclusion needs review')
            assert not (ROOT/'assets/vehicles'/id).exists(),(id,'Excluded vehicle retains assets')
            status='excluded-analogue'
        else:
            assert not row['active'],(id,'Active vehicle has neither profile nor exclusion')
            status='inactive'
        result.append({'vehicleId':id,'package':row['package'],'active':row['active'],'status':status,
                       **({'profile':'profiles/'+id+'.lua','layoutStatus':p.layoutStatus,
                           **evidence(id,p.layoutStatus),
                           'digits':len(p.fields),'auxiliaryDigits':len(p.auxiliaryFields or engine.table()),
                           'assets':sorted(assets)} if p else {})})
    return result


def main():
    rows=audit();active=[r for r in rows if r['active']]
    counts=Counter(r['status'] for r in active)
    (ROOT/'catalog/profile-coverage.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
    text=['# Dashboard profile coverage','',
          f'Against the saved live catalogue: **{len(active)} active official vehicles**, '
          f'**{counts["profile"]} bundled digital profiles**, **{counts["excluded-analogue"]} analogue exclusions**. '
          f'{len(rows)-len(active)} inactive entries are outside the active-vehicle target.','',
          'Every enabled profile is registered and its referenced background, fonts, gauges and icons exist as nonempty DDS files. '
          'The bundle runs without the game installation, raw captures or setup scripts.','',
          'Coverage does not establish visual fidelity. `geometry-unverified` uses readable mesh UVs; '
          '`bounds-unverified` estimates a rectangular screen from live mounted bounding spheres and digit transforms. '
          'The latter cannot recover UV crops or aspect ratios and needs visual calibration. '
          '`asset-calibrated-unverified` adds explicit digit anchors/sizes matched to the original artwork in sample previews; it has not been verified in each live car. '
          'Some warning/visibility/colour controls are not animated; missing telemetry displays `--`. '
          'Mixed cockpits expose only their original digital panel.','',
          'Regenerate and validate with `python tools/profile_coverage.py`. '
          'Raw scene bounds and archives remain ignored; only prepared runtime assets are bundled.','',
          'Capture method and runtime validation are listed separately. See [RUNTIME_AUDIT.md](RUNTIME_AUDIT.md) for findings.','',
          '| Vehicle ID | Package | Active | Coverage | Calibration | Live validation |',
          '| --- | --- | --- | --- | --- | --- |']
    for r in rows:
        id=r['vehicleId'];label=f'[{id}](../profiles/{id}.lua)' if r['status']=='profile' else f'`{id}`'
        text.append(f'| {label} | {r["package"]} | {"Yes" if r["active"] else "No"} | {r["status"]} | {r.get("calibrationStatus", "")} | {r.get("validationStatus", "")} |')
    (ROOT/'catalog/PROFILE_COVERAGE.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    print(f'Coverage passed: {len(active)} active vehicles; {counts["profile"]} profiles, {counts["excluded-analogue"]} analogue exclusions; all referenced assets present')


if __name__=='__main__':main()
