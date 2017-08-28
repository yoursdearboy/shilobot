import os
import time
from math import inf
from contextlib import contextmanager
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta
from tempfile import _get_candidate_names as get_tempfilename
from tempfile import _get_default_tempdir as get_tempdir

MAX_TIME = 60

class ReplyDists(dict):
  def __init__(self, a=0.15, b=0.1, *args, **kwargs):
    super(ReplyDists, self).__init__(*args, **kwargs)
    self.a = a
    self.b = b

  def __missing__(self, key):
    self[key] = (self.a, self.b)
    return self[key]

  def get(self, key):
    return self[key]

  def set(self, key, a, b):
    self[key] = (a,b)

  def cdf(self, x, key):
    a,b = self[key]
    return beta.cdf(x, a, b, scale=MAX_TIME)

  @contextmanager
  def plot(self, key):
    a,b = self[key]
    label = r"$\alpha=%.2f$ $\beta=%.2f$" % (a,b)
    xs = range(0,MAX_TIME+1)
    plt.figure()
    plt.plot(xs, self.cdf(xs, key), 'r-', label=label)
    plt.yticks(np.arange(0,1+0.1,0.1))
    plt.xticks(np.arange(0,MAX_TIME+1,5))
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    path = "%s/%s.png" % (get_tempdir(), next(get_tempfilename()))
    plt.savefig(path)
    yield path
    os.remove(path)

class ReplyTimes(dict):
  def __init__(self, dists, *args, **kwargs):
    super(ReplyTimes, self).__init__(*args, **kwargs)
    self.dists = dists

  def __missing__(self, key):
    return -inf

  def record(self, key):
    self[key] = time.time()

  def diff(self, key):
    timediff = (time.time() - self[key])/MAX_TIME
    return timediff

  def score(self, key):
    score = self.dists.cdf(self.diff(key), key)
    return score
