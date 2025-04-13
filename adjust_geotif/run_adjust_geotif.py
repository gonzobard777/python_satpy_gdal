from adjust_geotif import adjust_geotif
from constant import C

satName='a1'
channel='ch04'
timestamp='2025040111'

input_file_pattern=f"{C.ASSET_DIR}/{satName}_{timestamp}*_{channel}.tif"

output_file_path= f"{C.ASSET_DIR}/result/{satName}-{channel}-{timestamp}"
output_file=f"{output_file_path}.tif"
tmp_output_file = f"{output_file_path}_temp.tif"

adjust_geotif(
    input_file_pattern,
    output_file,
    tmp_output_file,
)

