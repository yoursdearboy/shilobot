import markovify

class Model:
  def __init__(self, songs, max_overlap_ratio=0.7, max_overlap_total=15):
    self.songs = songs
    text = "\n".join([song['lyrics'].strip() for song in songs if 'lyrics' in song])
    self.model = markovify.NewlineText(text, state_size=2)
    self.max_overlap_ratio = max_overlap_ratio
    self.max_overlap_total = max_overlap_total

  def speech(self):
    return self.model.make_sentence(
      max_overlap_ratio=self.max_overlap_ratio,
      max_overlap_total=self.max_overlap_total)
