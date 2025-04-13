from datetime import datetime, timedelta
from util.my_fs import *

target_dir='D:/_SAT/PLANETA_STEND/a1_ch04'
pattern='a1_*_ch04.tif'

copy_files('D:/_SAT/PLANETA_STEND/A',target_dir,pattern,)
# rename_files(target_dir,pattern,'20250401','20250413')

correct_dates(
    target_dir,
    datetime.fromisoformat('2025-04-13T21:00:00.000Z')-timedelta(hours=5),
    timedelta(minutes=15)
)

