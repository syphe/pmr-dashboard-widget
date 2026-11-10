"""Only publish profiles drawn from original dashboard assets."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIGITAL_ONLY={'Chevrolet_Corvette_C5R','Mazda_MX-5_Cup_2017','TA2_Chevrolet_Camaro_2024'}


def exclusion_reason(row):
    explicit=json.loads((ROOT/'catalog/exclusions.json').read_text())
    if row['id'] in explicit:return explicit[row['id']]
    if row.get('hasOriginalArtwork') is False:
        return 'No original display artwork resolved; replacement layouts are disabled.'
    # These mixed dashboards have a genuine digital panel. Keep that panel and
    # omit their analogue instruments rather than drawing replacement dials.
    if row['id'] in DIGITAL_ONLY:return None
    if any(w['type']=='rotator' for w in row['widgets']):
        return 'Analogue face/needle recreation removed; original face mapping required.'
    if row.get('recreatedPrimary'):
        return 'Custom replacement artwork removed; original display mapping required.'
    return None
