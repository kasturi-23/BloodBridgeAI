from copy import deepcopy


def serialize_doc(doc: dict):
    if not doc:
        return None
    out = deepcopy(doc)
    out.pop("_id", None)
    return out
