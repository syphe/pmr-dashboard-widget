"""Keep layout provenance separate from evidence gathered in a live game."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
CAPTURE_METHODS={'geometry-unverified':'mesh-uv','bounds-unverified':'mounted-bounds',
                 'geometry-calibrated-unverified':'mesh-uv-and-artwork',
                 'asset-calibrated-unverified':'mounted-bounds-and-artwork','hand-tuned':'live-motec-and-artwork'}


def evidence(id,layout_status,root=ROOT):
    path=root/'profiles'/(id+'.lua')
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    report=root/'catalog/runtime-audit.json'
    rows=json.loads(report.read_text()).get('vehicles',{}) if report.exists() else {}
    row=rows.get(id,{})
    fresh=row.get('profileSha256')==digest
    method=CAPTURE_METHODS.get(layout_status,'unknown')
    if id in {'Mazda_787B_1991','Toyota_GT-One_TS020'}:method='mesh-uv-and-artwork'
    return {'captureMethod':method,
            'calibrationStatus':'hand-tuned' if layout_status=='hand-tuned' else 'preview-calibrated' if layout_status in {'asset-calibrated-unverified','geometry-calibrated-unverified'} else 'generated',
            'validationStatus':row.get('validationStatus','pending-runtime-audit') if fresh else 'pending-runtime-audit',
            'sceneAuditStatus':row.get('sceneAuditStatus','pending') if fresh else 'pending',
            'auditFindings':row.get('findings',[]) if fresh else [],
            'auditCurrent':fresh,'profileSha256':digest}
