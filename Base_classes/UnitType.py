from enum import Enum
import json

class UnitType(Enum):
    inf = "inf"
    lanc = "lanc"
    mark = "mark"

    @classmethod
    def list(cls):
        return list(c for c in UnitType)


def _to_unitx(id_str):
    uid = id_str.upper()
    if "INF" in uid:
        return UnitType.inf
    if "LANC" in uid:
        return UnitType.lanc
    if "MARK" in uid:
        return UnitType.mark
    return None
    
def prettify(_UnitTypeJson, json_dump= True):
    _dict = { k.name : v for k,v in _UnitTypeJson.items() }
    if json_dump : return json.dumps(_dict, indent=2)
    else : return _dict

def very_prettify(_unit):
    return json.dumps({ k.name : prettify(v, json_dump=False) for k,v in _unit.items() }, indent=4)