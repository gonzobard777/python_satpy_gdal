from shutil import copy
from pathlib import Path

def copy_files(src_dir_path, dst_dir_path, files_pattern):
    src_dir=Path(src_dir_path)
    dst_dir=Path(dst_dir_path)
    dst_dir.mkdir(parents=True, exist_ok=True)
    for file in src_dir.glob(files_pattern):
        copy(str(file), dst_dir/file.name)


def rename_files(dir_path,files_pattern,old_substr,new_substr):
    dir = Path(dir_path)
    for file in dir.glob(files_pattern):
        name=file.name.replace(old_substr, new_substr)
        file.rename(dir/name)


def correct_dates(
        dir_path,  # папка с файлами
        dtime,     # начать с этого времени
        time_step, # на каждой след. итерации прибавлять ко времени такой шаг
        time_format="%Y%m%d%H%M%S" # в таком формате в имени файла указано время
):
    directory=Path(dir_path)
    for file in directory.glob('*'):
        old=file.name.split("_")[1]
        new=dtime.strftime(time_format)
        name=file.name.replace(old, new)
        file.rename(directory/name)
        dtime=dtime+time_step
