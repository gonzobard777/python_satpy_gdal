from pathlib import Path

def tmp_filepath(original_path: str) -> str:
    """Возвращает абсолютный путь до временного файла,
       находящегося в той же папке, что и оригинальный файл.
    Args:
        original_path: абсолютный путь до файла
    """
    path = Path(original_path)
    return str(path.parent / f"{path.stem}_tmp{path.suffix}")
