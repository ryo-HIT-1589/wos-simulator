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
    
def prettify(_dict, precision= 2, _json= False):
    if _json: return { k.name : v for k,v in _dict.items() }
    else : 
        return ' / '.join("{}".format(round(_dict[v],precision)) for v in UnitType)
