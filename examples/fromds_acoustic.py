import os
import sys
import argparse
from typing import Optional, Tuple

# Импорт библиотек
try:
    import acoustid
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, TRCK, APIC, error
    import audioread
except ImportError as e:
    print("Ошибка: Не установлены зависимости.")
    print("Выполните: pip install mutagen pyacoustid audioread")
    sys.exit(1)

# Конфигурация
API_KEY = "ВАШ_КЛЮЧ_ACOUSTID"  # Зарегистрируйтесь на https://acoustid.org/

def get_track_metadata(file_path: str) -> Optional[Tuple[str, str, str, str]]:
    """
    Использует акустический отпечаток (как Shazam) для поиска метаданных.
    Возвращает: (Название, Исполнитель, Альбом, Год) или None.
    """
    try:
        print(f"  🔍 Анализ отпечатка: {os.path.basename(file_path)}")
        # Генерируем отпечаток и ищем в базе AcoustID
        # timeout=30 важен для больших файлов или медленного интернета
        results = acoustid.match(API_KEY, file_path, timeout=30)
        
        # results это генератор, берем первый (самый точный) результат
        for score, recording_id, title, artist in results:
            if score > 0.5:  # Проверяем, что точность выше 50%
                print(f"  ✅ Найдено совпадение (Score: {score:.2f})")
                # Дополнительно пытаемся достать альбом и год через отдельный запрос (опционально)
                # Упростим: в базовом match нет альбома, нужно доп. API, но для демо:
                album = "Unknown Album"
                year = ""
                # Попробуем найти детали через музыку (не обязательно для MVP)
                return (title, artist, album, year)
            else:
                print(f"  ⚠️ Низкая точность совпадения ({score:.2f}), пропускаем.")
                return None
                
    except acoustid.FingerprintGenerationError:
        print(f"  ❌ Не удалось сгенерировать отпечаток (файл поврежден или слишком короткий).")
    except acoustid.WebServiceError as e:
        print(f"  ❌ Ошибка соединения с Acoustid API: {e}")
    except Exception as e:
        print(f"  ❌ Непредвиденная ошибка: {e}")
    return None

def write_id3_tags(file_path: str, metadata: dict):
    """
    Записывает ID3v2 теги в MP3 файл.
    """
    try:
        # Пытаемся загрузить существующие теги, если нет — создаем новый контейнер ID3
        try:
            audio = ID3(file_path)
        except error:
            # Файл существует, но тегов нет — создаем новый объект
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
        
        # Год (TDRC) — ID3v2.4 использует TDRC вместо TYER
        if metadata.get('year'):
            audio.add(TDRC(encoding=3, text=metadata['year']))
        
        # Жанр (TCON)
        if metadata.get('genre'):
            audio.add(TCON(encoding=3, text=metadata['genre']))
        
        # Сохраняем изменения в файл
        audio.save(file_path, v2_version=3)  # v2_version=3 для совместимости с Windows/iPhone
        print(f"  💾 Теги записаны для: {metadata.get('title')}")
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка записи тегов: {e}")
        return False

def process_folder(folder_path: str, force: bool = False):
    """
    Основной цикл: обходит папку, ищет MP3 без тегов и заполняет их.
    """
    if not os.path.isdir(folder_path):
        print("Указанная папка не найдена.")
        return

    mp3_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp3')]
    print(f"📁 Найдено MP3 файлов: {len(mp3_files)}")
    
    for filename in mp3_files:
        full_path = os.path.join(folder_path, filename)
        
        # 1. Проверяем, есть ли уже теги
        try:
            audio = MP3(full_path, ID3=ID3)
            has_tags = bool(audio.tags)
            if has_tags and not force:
                print(f"⏭️  Пропускаем (уже есть теги): {filename}")
                continue
        except:
            # Если файл кривой или нет тегов — идем дальше
            pass
        
        # 2. Ищем метаданные через Shazam-подобный алгоритм
        meta = get_track_metadata(full_path)
        
        if meta:
            title, artist, album, year = meta
            write_id3_tags(full_path, {
                'title': title,
                'artist': artist,
                'album': album,
                'year': year
            })
        else:
            print(f"  ❌ Не найдено в базе: {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Автоматическая простановка ID3 тегов через акустический отпечаток (Shazam/Chromaprint).")
    parser.add_argument("folder", help="Путь к папке с MP3 файлами")
    parser.add_argument("--force", action="store_true", help="Перезаписать существующие теги")
    args = parser.parse_args()
    
    if API_KEY == "ВАШ_КЛЮЧ_ACOUSTID":
        print("⚠️  ВНИМАНИЕ: Укажите свой API ключ Acoustid внутри скрипта (переменная API_KEY).")
        print("   Получить бесплатно: https://acoustid.org/")
        sys.exit(1)
        
    process_folder(args.folder, args.force)