#!/usr/bin/env python
import concurrent.futures
from yamusic import Artist
from ruamel import yaml

def fetch_songs(_id):
  artist = Artist.find(_id)
  songs = artist.songs
  # Disable concurrency because of Yandex Music with Selenium
  with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    futures = [executor.submit(lambda s: s.lyrics, song) for song in songs]
    concurrent.futures.as_completed(futures)
  return songs

def song_dsl(song):
  out = ["- id: %s" % song.id, 
         "  title: %s" % song.title,
         "  link: %s" % song.link,
         "  album:",
         "    id: %s" % song.album.id,
         "    title: %s" % song.album.title,
         "    link: %s" % song.album.link]

  if song.lyrics:
    out.append("  lyrics: |")
    for line in song.lyrics.split("\n"):
      out.append("    %s" % line)

    out.append("  quotes:")
    for line in song.lyrics.split("\n"):
      line = line.strip()
      if len(line) == 0:
        continue
      if ":" in line:
        line = "\"%s\"" % line
      out.append("    - %s" % line)

  return "\n".join(out)

def make_dsl(songs):
  return "\n".join([song_dsl(song) for song in songs])

def write_dsl(songs, file_path):
  with open(file_path, 'w') as f:
    f.write(make_dsl(songs))

def read_dsl(file_path):
  with open(file_path, 'r') as f:
    return yaml.load(f, Loader=yaml.Loader)

if __name__ == '__main__':
  from argparse import ArgumentParser

  parser = ArgumentParser(description="Create shilobot db")
  parser.add_argument('--action', choices=['download', 'list'])
  parser.add_argument('--artist-id', help="Artist id")
  parser.add_argument('--db-file', default='db.yaml', help="YAML file to store db")
  args = parser.parse_args()

  if args.action == 'download' and not args.artist_id:
    parser.error('--action download requires --artist-id')

  if args.action == 'download':
    write_dsl(
      fetch_songs(args.artist_id),
      args.db_file)
  elif args.action == 'list':
    db = read_dsl(args.db_file)
    for song in db:
      print(song['title'])
  else:
    parser.print_help()
