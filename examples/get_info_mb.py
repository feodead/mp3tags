import musicbrainzngs
#import argparse

musicbrainzngs.set_useragent("feodeadApp", "0.1", "misc@kromas.pw")
musicbrainzngs.set_hostname("musicbrainz.org")

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
      
def main():

    print(get_track_language_musicbrainz("Идем на восток", "Ногу Свело"))

if __name__ == "__main__":
    main()