import os
import asyncio
import argparse
from typing import Optional, Dict, Any

# Импорт библиотек
try:
    from MelodyMaster import Shazam, Serialize
    import musicbrainzngs
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, TLAN, COMM, error
except ImportError as e:
    print("Ошибка: Не установлены зависимости.")
    print("Выполните: pip install MelodyMaster mutagen")
    print("Примечание: MelodyMaster требует Python 3.8+")
    raise e

musicbrainzngs.set_useragent("feodeadApp", "0.1", "misc@kromas.pw")
musicbrainzngs.set_hostname("musicbrainz.org")

# Функция, разделяющая имя файла на Исполнителя и Название
def split_string(s):
    artist, rest = s.split(" - ", 1)
    title = rest.rsplit(".", 1)[0]
    return artist, title

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
        language = get_track_language_musicbrainz(serialized.title, serialized.subtitle)
        if language == None:
            print(f"  🎵 Не нашли язык трека по данным от Shazam. Ищем по имени файла")
            fartist, ftitle = split_string(file_path)
            print(f"  🎵 {fartist} - {ftitle}")
            language = get_track_language_musicbrainz(ftitle, fartist)
        if language == None:
            print(f"  ❌ Не получилось найти язык трека")
            
        metadata = {
                'title': serialized.title,
                'artist': serialized.subtitle,
                'album': track_album if track_album != '' else serialized.title,
                'year': track_year,
                'genre': track_genre,
                'language': language if language != None else '',
                'cover_url': result['track'].get('images', {}).get('coverart', '')
            }
        return metadata
    except Exception as e:
        print(f"  ❌ {file_path}: Ошибка при распознавании: {e}")
        return None

def get_track_language_musicbrainz(track_name, artist_name):
    """Поиск языка в MusicBrainz"""
    try:
        result = musicbrainzngs.search_recordings(
            query=f"recording:{track_name} AND artist:{artist_name}",
            limit=1
        )
        if result['recording-list']:
            reid = result['recording-list'][0]['release-list'][0]['id']
            release_result = musicbrainzngs.search_releases(query=f"reid:{reid}", limit=1)
            if release_result['release-list']:
              language = release_result['release-list'][0]['text-representation']['language']
              return language
        return None
    except Exception as e:
        print(f"MusicBrainz error: {e}")
        return None

def write_id3_tags(file_path: str, metadata: Dict[str, str], args):
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
        if metadata.get('title') and args.title:
            audio.add(TIT2(encoding=3, text=metadata['title']))
        
        # Исполнитель (TPE1)
        if metadata.get('artist') and args.artist:
            audio.add(TPE1(encoding=3, text=metadata['artist']))
        
        # Альбом (TALB)
        if metadata.get('album') and args.album:
            audio.add(TALB(encoding=3, text=metadata['album']))
        
        # Год (TDRC) — ID3v2.4
        if metadata.get('year') and args.year:
            audio.add(TDRC(encoding=3, text=metadata['year']))
        
        # Жанр (TCON)
        if metadata.get('genre') and args.genre:
            audio.add(TCON(encoding=3, text=metadata['genre']))
        
        # Язык текста (TLAN)
        if metadata.get('language') and args.language:
            audio.add(TLAN(encoding=3, text=metadata['language']))
        
        # Комментарий (COMM)
        audio.add(COMM(encoding=3, text="AutoTagged"))
        
        # Сохраняем изменения
        audio.save(file_path, v2_version=3)  # v2_version=3 для совместимости
        print(f"  💾 Теги сохранены: {metadata.get('title', 'Unknown')}")
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка записи тегов: {e}")
        return False

async def process_file(file_path: str, args) -> bool:
    """
    Обрабатывает один MP3 файл.
    """
    if not os.path.basename(file_path).lower().endswith('.mp3'):
        print(f"  ❌ {os.path.basename(file_path)}: не mp3 файл!")
        return False

    metadata = await recognize_track(file_path)
    
    if metadata and metadata.get('title') and metadata.get('artist'):
        return write_id3_tags(file_path, metadata, args)
    else:
        print(f"  ❌ Не удалось получить данные для: {os.path.basename(file_path)}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Автоматическая простановка ID3 тегов через Shazam (MelodyMaster).\n"
                    "Программа распознаёт треки по аудио и заполняет теги mp3 файлов.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("file", help="Путь к mp3 файлу")
    parser.add_argument('-t', '--title', action="store_true", help="Изменить название трека (TIT2)")
    parser.add_argument('-a', '--artist', action="store_true", help="Изменить исполнителя (TPE1)")
    parser.add_argument('-m', '--album', action="store_true", help="Изменить альбом (TALB)")
    parser.add_argument('-y', '--year', action="store_true", help="Изменить год (TDRC)")
    parser.add_argument('-g', '--genre', action="store_true", help="Изменить жанр (TCON)")
    parser.add_argument('-l', '--language', action="store_true", help="Изменить язык (TLAN)")
    args = parser.parse_args()
    
    print("=" * 50)
    print("🎵 mp3 Tag Filler with Shazam (MelodyMaster)")
    print("=" * 50)
    print(f"🎵 Файл: {args.file}")
    print("-" * 50)
    
    # Запускаем асинхронную обработку
    asyncio.run(process_file(args.file, args))

if __name__ == "__main__":
    main()