import string
from itertools import chain
import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import cdist

stopwords = nltk.corpus.stopwords.words('russian')
lines_tokenizer = nltk.tokenize.simple.LineTokenizer()
words_tokenizer = nltk.tokenize.simple.SpaceTokenizer()
stemmer = nltk.stem.snowball.SnowballStemmer('russian')
  
def split_in_lines(text):
  lines = lines_tokenizer.tokenize(text)
  return lines

filter_chars = string.punctuation + "«»–…"
def process_line(line):
  line = ''.join(filter(lambda x: x not in filter_chars, line))
  words = words_tokenizer.tokenize(line)
  words = [process_word(word) for word in words if word.lower() not in stopwords and len(word) > 2]
  words = [word for word in words if len(word) > 2 and not word.isdigit()]
  return words

def ngrams(words):
  min = 4
  max = 6
  ngrams = chain(*[nltk.ngrams(word, i) for i in range(min, max+1) for word in words])
  ngrams = [''.join(ngram) for ngram in ngrams]
  return ngrams

def process_word(word):
  word = word.lower()
  word = word.strip()
  word = stemmer.stem(word)
  return word

# TODO: Score requires some correction
# TODO: But first get normal quotes
class Model:
  def __init__(self, songs):
    self.songs = songs
    self.quotes = [q for song in songs if 'quotes' in song for q in song['quotes']]
    self.tfidf = TfidfVectorizer(strip_accents='unicode', tokenizer=lambda t: process_line(t))
    self.tfs = self.tfidf.fit_transform(self.quotes).toarray()
    self.vocabulary = dict([(k,v) for k,v in self.tfidf.vocabulary_.items()])

  def search(self, line):
    res = self.tfidf.transform([line]).toarray()
    dists = cdist(res, self.tfs, 'cosine')
    idx = np.nanargmin(dists) if not np.isnan(dists).all() else 0
    score = dists[0,idx]
    quote = None if np.isnan(score) else self.quotes[idx]
    res2 = self.tfs[idx]
    return (score, quote)

  def terms(self, line1, line2):
    return set(process_line(line1)) & set(process_line(line2))
