import os

def remove_existed_file(path2file:str):
    if os.path.exists(path2file):
        os.remove(path2file)