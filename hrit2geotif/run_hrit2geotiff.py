from hrit2geotif import hrit_to_geotiff
from constant import C


### MSG

datetime_str='20250401'
hour='09'

sat_id=1
sat_name='MSG2'

# sat_id=2
# sat_name='MSG3'

# hrit_to_geotiff(
#     f'{C.HRIT}/{datetime_str}',
#     f"{datetime_str}{hour}00",
#     sat_id,
#     ["hrv_severe_storms_blue_masked"], # VIS
#     f"{C.ASSET_DIR}/result/{sat_name}"
# )


### Himawari

datetime_str='20250409'
hour='03'
hrit_to_geotiff(
    f'{C.HRIT}/himawari/{datetime_str}',
    f"{datetime_str}{hour}00",
    3,
    ['hrv_severe_storms_blue_masked'], # VIS B03
    f"{C.ASSET_DIR}/result/Himawari"
)
