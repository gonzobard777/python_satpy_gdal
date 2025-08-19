from constant import C
from south_up_2_north_up import south_up_2_north_up

filename="MSG3_VIS006-20250401_1200.tif"
input_file=f"{C.ASSET_DIR}/{filename}"
output_file=f"{C.ASSET_DIR}/delete_me/MSG3_VIS006-20250401_1200.tif"

south_up_2_north_up(input_file,output_file)