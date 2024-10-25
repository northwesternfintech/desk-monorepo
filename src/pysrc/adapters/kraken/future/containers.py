from pysrc.util import exceptions

def safe_at(list, idx):
    if idx < 0 or idx >= len(list):
        return exceptions.DIE("Safe at failed due to index out of bounds")        
    return list[idx]

def get_single(list):
    if len(list) != 1:
        return exceptions.DIE("Get single failed due to list not having exactly one element")
    return list[0]