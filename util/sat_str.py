from contract import ProjType

def sat_str(proj: ProjType):
    result='unknown_proj'
    if proj==ProjType.Mercator: result='mercator'
    if proj==ProjType.StereoNorth: result='stereonorth'
    return result