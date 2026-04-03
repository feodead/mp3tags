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
API_KEY = ""  # Зарегистрируйтесь на https://acoustid.org/

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
        #for value in results: print(f"{value}")
        # results это генератор, берем первый (самый точный) результат
        for score, recording_id, title, artist in results:
            if score > 0.5:  # Проверяем, что точность выше 50%
                print(f"  ✅ Найдено совпадение (Score: {score:.2f})")
                # Дополнительно пытаемся достать альбом и год через отдельный запрос (опционально)
                # Упростим: в базовом match нет альбома, нужно доп. API, но для демо:
                #album = "Unknown Album"
                #year = ""
                print(artist, title, recording_id)
                # Попробуем найти детали через музыку (не обязательно для MVP)
                return (title, artist)
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Автоматическая простановка ID3 тегов через акустический отпечаток (Shazam/Chromaprint).")
    parser.add_argument("file_path", help="Путь к папке с MP3 файлами")
    args = parser.parse_args()
    
    if API_KEY == "ВАШ_КЛЮЧ_ACOUSTID":
        print("⚠️  ВНИМАНИЕ: Укажите свой API ключ Acoustid внутри скрипта (переменная API_KEY).")
        print("   Получить бесплатно: https://acoustid.org/")
        sys.exit(1)
        
    get_track_metadata(args.file_path)