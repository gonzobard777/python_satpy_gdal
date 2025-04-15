import shutil
from datetime import datetime, timedelta
from util.my_fs import *

dtime=datetime.fromisoformat('2025-04-15T08:00:00.000Z')-timedelta(hours=5)

'''
    Генерация из исходников
    в папке A лежат два спутника a1 и a2
    в папке E лежат спутники: e2,e3,4
'''
# base_dir_path='D:/_SAT/PLANETA_STEND'
# mock_dir_path=f'{base_dir_path}/mock_data' # папка с результирующими папками/файлами
# metadata=[
#     ['a1','ch04',f'{base_dir_path}/A'],
#     ['a2','ch04',f'{base_dir_path}/A'],
#     ['e2','ch04',f'{base_dir_path}/E'],
#     ['e3','ch04',f'{base_dir_path}/E'],
#     ['e4','ch04',f'{base_dir_path}/E'],
# ]
#
# shutil.rmtree(mock_dir_path)
# for sat,channel,src_dir_path in metadata:
#     target_dir=f'{mock_dir_path}/{sat}_{channel}'
#     pattern = f'{sat}_*_{channel}.tif'
#     copy_files(src_dir_path,target_dir,pattern)
#     # rename_files(target_dir,pattern,'20250401','20250413')
#     correct_dates(
#         target_dir,
#         dtime,                # начать с этого времени
#         timedelta(minutes=15) # потом прибавлять этот шаг
#     )


'''
    Перегенерация на новый день
    в каждой папке лежат файлы для одного спутника
'''
base_dir_path='D:/_SAT/PLANETA_STEND/predgenerated'
metadata=[
    ['a1','ch04',f'{base_dir_path}'],
    ['a2','ch04',f'{base_dir_path}'],
    ['e2','ch04',f'{base_dir_path}'],
    ['e3','ch04',f'{base_dir_path}'],
    ['e4','ch04',f'{base_dir_path}'],
]
for sat,channel,src_dir_path in metadata:
    target_dir = f'{src_dir_path}/{sat}_{channel}'
    pattern = '*'
    correct_dates(
        target_dir,
        dtime,                # начать с этого времени
        timedelta(minutes=15) # потом прибавлять этот шаг
    )

