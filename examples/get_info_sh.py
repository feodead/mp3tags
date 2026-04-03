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

async def recognize_track(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Распознаёт трек через Shazam (MelodyMaster) по аудиофайлу.
    Возвращает словарь с метаданными или None.
    """
    try:
        print(f"  🎵 Распознаём: {os.path.basename(file_path)}")
        shazam = Shazam(language='ru-RU')
        #shazam = Shazam()
        result = await shazam.recognize(file_path)
        serialized = Serialize.track(data=result['track'])
        track_album=''
        track_year=''
        track_genre=''
        if 'genres' in result['track'] and result['track']['genres'].get('primary'):
                track_genre = result['track']['genres']['primary']
        for section in serialized.sections[0].metadata:
            if section.title.lower() == "альбом" or section.title.lower() == "album":
                track_album = section.text
            if section.title.lower() == "выпущено" or section.title.lower() == "released":
                track_year = section.text
        metadata = {
                'title': serialized.title,
                'artist': serialized.subtitle,
                'album': track_album,
                'year': track_year,
                'genre': track_genre,
                'cover_url': result['track'].get('images', {}).get('coverart', '')
            }
        print(result)
        print("=" * 50)
        print(metadata)
        return metadata
    except Exception as e:
        print(f"  ❌ {file_path}: Ошибка при распознавании: {e}")
        return None

def main():

    parser = argparse.ArgumentParser(
        description="Автоматическая простановка ID3 тегов через Shazam (MelodyMaster).\n"
                    "Программа распознаёт треки по аудио и заполняет теги MP3 файлов.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("file_path", help="Путь к папке с MP3 файлами")

    args = parser.parse_args()
    
    #file = Path(args.file_path)

    asyncio.run(recognize_track(args.file_path))

if __name__ == "__main__":
    main()