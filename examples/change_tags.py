import os
import asyncio
import argparse
from typing import Optional, Dict, Any
from pathlib import Path

# Импорт библиотек
try:
    from MelodyMaster import Shazam, Serialize
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, error
except ImportError as e:
    print("Ошибка: Не установлены зависимости.")
    print("Выполните: pip install MelodyMaster mutagen")
    print("Примечание: MelodyMaster требует Python 3.8+")
    raise e

metadata={'title': 'Идем на восток!', 'artist': 'Nogu Svelo!', 'album': 'Идем на восток!', 'year': '2005', 'genre': 'Rock', 'cover_url': 'https://is1-ssl.mzstatic.com/image/thumb/Music116/v4/03/f9/6a/03f96ac9-c00d-e489-a7b4-2529abda558b/888003994386_cover.jpg/400x400cc.jpg'}

def write_id3_tags(file_path: str, metadata: Dict[str, str]):
    """
    Записывает ID3v2 теги в MP3 файл.
    """
    try:
        # Пытаемся загрузить существующие теги, если нет — создаём новый контейнер
        try:
            audio = ID3(file_path)
        except error:
            audio = ID3()
        
        # Название (TIT2)
        if metadata.get('title'):
            audio.add(TIT2(encoding=3, text=metadata['title']))
        
        # Исполнитель (TPE1)
        if metadata.get('artist'):
            audio.add(TPE1(encoding=3, text=metadata['artist']))
        
        # Альбом (TALB)
        if metadata.get('album'):
            audio.add(TALB(encoding=3, text=metadata['album']))
        
        # Год (TDRC) — ID3v2.4
        if metadata.get('year'):
            audio.add(TDRC(encoding=3, text=metadata['year']))
        
        # Жанр (TCON)
        if metadata.get('genre'):
            audio.add(TCON(encoding=3, text=metadata['genre']))
        
        audio.add
        
        # Сохраняем изменения
        audio.save(file_path, v2_version=3)  # v2_version=3 для совместимости
        print(f"  💾 Теги сохранены: {metadata.get('title', 'Unknown')}")
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка записи тегов: {e}")
        return False
      
def main():

    parser = argparse.ArgumentParser(
        description="Автоматическая простановка ID3 тегов через Shazam (MelodyMaster).\n"
                    "Программа распознаёт треки по аудио и заполняет теги MP3 файлов.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("file_path", help="Путь к папке с MP3 файлами")

    args = parser.parse_args()
    
    #file = Path(args.file_path)

    write_id3_tags(args.file_path)

if __name__ == "__main__":
    main()