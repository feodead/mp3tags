import os
import asyncio
import argparse
from typing import Optional, Dict, Any
from pathlib import Path
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, TLAN, COMM, error

def read_id3_tags(file_path: str):
  #audio = MP3(file_path)
  #print(audio.info.length)
  #print(audio.info.bitrate)
  print(mutagen.File(file_path))

def main():

    parser = argparse.ArgumentParser(
        description="Автоматическая простановка ID3 тегов через Shazam (MelodyMaster).\n"
                    "Программа распознаёт треки по аудио и заполняет теги MP3 файлов.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("file_path", help="Путь к папке с MP3 файлами")

    args = parser.parse_args()
    
    #file = Path(args.file_path)

    read_id3_tags(args.file_path)

if __name__ == "__main__":
    main()