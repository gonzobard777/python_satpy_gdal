import glob
from satpy import config
from satpy.scene import Scene
from hrit2geotif.hrit2geotif import save_scene_datasets
from constant import C

filename='a1_20250401110000_ch04'

fnames = glob.glob(f"{C.ASSET_DIR}/{filename}*tif")
config.set(config_path=[C.CONFIG_DIR])
scn = Scene(reader='generic_image', filenames=fnames)

datasets =['image']
scn.load(wishlist=datasets)

save_scene_datasets(scn, f'{C.ASSET_DIR}/{filename}_adjusted', datasets, '1', '')
