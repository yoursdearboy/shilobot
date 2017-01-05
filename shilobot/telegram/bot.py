#!/usr/bin/env python
import os, sys, time, logging
from telegram.ext import Updater, CommandHandler, MessageHandler, InlineQueryHandler, Filters
from shilobot.db import read_dsl
from shilobot.fts import Model as FTSModel
from shilobot.reply_dist import ReplyDists, ReplyTimes

def setup_logger():
  file_path = os.path.join(os.getcwd(), 'bot.log')
  logging.basicConfig(filename=file_path, level=logging.DEBUG)
  logger = logging.getLogger(__name__)
  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

  stdout = logging.StreamHandler()
  stdout.setLevel(logging.INFO)
  stdout.setFormatter(formatter)
  logger.addHandler(stdout)

  # file = logging.FileHandler(file_path)
  # file.setLevel(logging.DEBUG)
  # file.setFormatter(formatter)
  # logger.addHandler(file)

  return logger
logger = setup_logger()

songs = read_dsl('db.yaml')
fts = FTSModel(songs)

# === Hello part ===
HELLO_MSG = """
Я тут посижу послушаю, покурю, понюхаю.
"""

def start(bot, update):
  update.message.reply_text(HELLO_MSG)

echo_dists = ReplyDists()
echo_times = ReplyTimes(echo_dists)

ECHO_DIST_MSG = """
Отправьте два числовых параметра α и β разделенных пробелом
"""
def echo_dist(bot, update):
  chat_id = update.message.chat.id

  inp = update.message.text.split(' ')
  if len(inp) == 3:
    try:
      a = float(inp[1])
      b = float(inp[2])
    except ValueError:
      update.message.reply_text(ECHO_DIST_MSG)
      return
    echo_dists.set(chat_id, a, b)

  a,b = echo_dists.get(chat_id)
  with echo_dists.plot(chat_id) as path:
    logger.debug("Sending echo distribution photo at path %s" % path)
    with open(path, 'rb') as photo:
      update.message.reply_photo(photo=photo, caption="α=%.2f β=%.2f\n%s" % (a,b, ECHO_DIST_MSG))

MIN_ECHO_LENGTH = 6
def echo(bot, update):
  inp = update.message.text
  chat_id = update.message.chat.id
  username = update.message.from_user.username
  logger.debug("Quote from %s" % username)

  if len(inp) < MIN_ECHO_LENGTH:
    logger.debug("Was skept because of length")
    return

  score, outp = fts.search(inp)
  logger.debug("Has score %s" % score)
  if outp is None or score > 0.5:
    logger.debug("Was skept")
    return

  time_diff = echo_times.diff(chat_id)
  time_score = echo_times.score(chat_id)
  logger.debug("Has time score %.2f" % time_score)
  if score > time_score:
    logger.debug("Was skept")
    logger.debug("IN: %s" % inp)
    logger.debug("OUT: %s" % outp)
    return

  echo_times.record(chat_id)
  update.message.reply_text(outp)

def error(bot, update, error):
  logger.warn('Update "%s" caused error "%s"' % (update, error))

def main(token):
  updater = Updater(token)
  dp = updater.dispatcher
  dp.add_handler(CommandHandler("start", start))
  dp.add_handler(CommandHandler("echodist", echo_dist))
  dp.add_handler(MessageHandler(Filters.text, echo))
  dp.add_error_handler(error)
  updater.start_polling()
  logger.info("Starting bot loop")
  updater.idle()

if __name__ == '__main__':
  if 'TOKEN' not in os.environ:
    sys.exit("Set TOKEN env variable")
  main(os.environ['TOKEN'])
