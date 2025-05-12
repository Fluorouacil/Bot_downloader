import os
import shutil

async def check_path(file_path: str):
    # Если переданный file_path не имеет расширения .mp4 или .mp3, ищем подходящий файл в директории
    if not (file_path.lower().endswith(".mp4") or file_path.lower().endswith(".mp3")):
        dir_path = os.path.dirname(file_path)
        # Сначала пытаемся найти файл .mp4
        mp4_files = [f for f in os.listdir(dir_path) if f.lower().endswith(".mp4")]
        if mp4_files:
            file_path = os.path.join(dir_path, mp4_files[0])
            print(f"Найден mp4 файл: {file_path}")
        else:
            # Если не найден, пытаемся найти файл .mp3
            mp3_files = [f for f in os.listdir(dir_path) if f.lower().endswith(".mp3")]
            if mp3_files:
                file_path = os.path.join(dir_path, mp3_files[0])
                print(f"Найден mp3 файл: {file_path}")
            else:
                print(f"Файл с расширением .mp4 или .mp3 не найден в директории: {dir_path}")
                return
    return file_path

async def delete_file(file_path: str):
    folder = os.path.dirname(file_path)
    try:
        shutil.rmtree(folder)
        print(f"Папка '{folder}' успешно удалена.")
    except Exception as e:
        print(f"Ошибка при удалении папки '{folder}': {e}")