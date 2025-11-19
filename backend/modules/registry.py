from typing import List
from core.pipeline import Step

from modules.steps.cleaning import run as _clean
from modules.steps.integrity import run as _integrity
from modules.steps.ml_geocode import run as _ml
from modules.steps.here_geocode import run as _here
from modules.steps.geospatial import run as _geo
from modules.steps.fuse_confidence import run as _fuse
from modules.steps.anomaly import run as _anomaly
from modules.steps.self_heal import run as _heal


def default_steps() -> List[Step]:
    return [
        _clean,       # clean_address
        _integrity,   # integrity
        _ml,          # ml_geocode
        _here,        # here_geocode
        _geo,         # geospatial_checks
        _fuse,        # fuse_confidence
        _anomaly,     # anomaly_detection
        _heal,        # self_heal
    ]
