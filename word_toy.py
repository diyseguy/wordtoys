import sys
from optparse import OptionParser
import random

cmdln_args = " ".join(sys.argv)
op = OptionParser()
op.add_option("-n", "--num", dest="num_words", help="number of words to output", default=10)
op.add_option("-r", "--random_output_size", dest="random_out", help="output a randum number of words up to num_words",
              default=False,
              action="store_true")
op.add_option("-f", "--file", dest="file_name", help="prose text to pull words from")
op.add_option("-b", "--blacklist", dest="blacklist", help="blacklisted words")
op.add_option("-p", "--probabilities", dest="use_probabilities", default=True, action="store_true",
              help="Use probabilistic mapping between words")

(options, args) = op.parse_args()
num_words = int(options.num_words)
use_probabilities = options.use_probabilities
random_out = options.random_out
prose_txt = options.file_name
black_list = options.blacklist

class Word():
  def __init__(self, word, count, probability, id):
    self.id = id
    self.word = word
    self.count = count
    self.prob = probability

  def increment(self):
    self.count += 1


class WordToy():
  include_phrase_ends = False
  include_sentence_ends = True

  strip_chars = '".,?;:)(!<>@#$%^&*-_+=[]{}|/\\~`\n\r'
  phrase_ender = ',:()'
  sentence_ender = '.!'
  nothing = Word("zz",0,0,"zz".__hash__())
  sentence_end = Word(". ",0,0,". ".__hash__())
  phrase_end = Word(", ",0,0,", ".__hash__())

  def __init__(self, *args, **kwargs):
    self.blacklist = set()
    self.word_counts = {}  # word_id to (word, probability, count, id)
    self.words_in_order = None  # temporary data structure used to generate ngrams
    self.next_words = {}
    black_list_file = kwargs.pop('black_list_file', None)
    generate_word_order_list = kwargs.pop('generate_word_order_list', None)
    prose_file_name = kwargs.pop('prose_file', None)
    prose_txt = kwargs.pop('prose_txt', None)
    self.include_phrase_ends = kwargs.pop('include_phrase_ends', False)
    self.include_sentence_ends = kwargs.pop('include_sentence_ends', True)
    if black_list_file:
      self._load_black_list(black_list_file)
    if generate_word_order_list:
      self.words_in_order = []
    if prose_file_name:
      self._parse_prose_file(prose_file_name)
    elif prose_txt:
      self._parse_prose_txt(prose_txt)
    self._post_process_words()

  def _load_black_list(self, black_list_file):
    if black_list_file:
      bf = open(black_list_file, 'r')
      for line in bf:
        line = line.strip()
        self.blacklist.add(line)

  def _parse_prose_file(self, prose_file_txt):
    f = open(prose_file_txt, 'r')
    for line_num, line in enumerate(f):
      if line_num == 32:
        foo = 1
      words = line.strip().split(' ')
      self._parse_words(words)

  def _parse_prose_txt(self, prose_txt):
    lines = prose_txt.split('\n')
    for line in lines:
      words = line.strip().split(' ')
      self._parse_words(words)

  def _parse_words(self, words):
    last_word_id = None
    # for word in words:
    for count, word in enumerate(words):
      try:
        word_id, extra_id = self._add_word_to_word_map(word)
      except Exception as ex:
        foo = 1
      if not word_id:
        # was: if not word_id and not extra_id:
        continue
      if last_word_id:
        self.add_next_word(last_word_id, word_id)
      last_word_id = word_id
      if extra_id:
        self.add_next_word(last_word_id, extra_id)
        last_word_id = extra_id

  def _add_word_to_word_map(self, word):
    word, extra = WordToy.canonicalize_word(word)
    if not word and not extra:
      return None, None
    if word in self.blacklist:
      return None, self._add_word(extra)
    word_hash = self._add_word(word)
    extra_hash = self._add_word(extra)
    return word_hash, extra_hash

  def _add_word(self, word):
    if not word:
      return None
    word_hash = word.__hash__()
    if word_hash in self.word_counts:
      self.word_counts[word_hash].increment()
    else:
      self.word_counts[word_hash] = Word(word, 1, 0, word_hash)
    if self.words_in_order:
      self.words_in_order.append(word_hash)
    return word_hash

  def add_next_word(self, first_word_id, second_word_id):
    if first_word_id is None or second_word_id is None:
      foo = 1
    if first_word_id not in self.next_words:
      self.next_words[first_word_id] = {second_word_id: 0}
    nexts = self.next_words[first_word_id]
    if second_word_id not in nexts:
      nexts[second_word_id] = 0
    val = nexts[second_word_id]
    nexts[second_word_id] = val + 1

  def _post_process_words(self):
    num_words = len(self.word_counts)
    if num_words < 1:
      return
    for word_hash, word in self.word_counts.items():
      count = word.count
      prob = float(count) / float(num_words)
      word.prob = prob

  @classmethod
  def canonicalize_word(cls,word):
    if not word or len(word) < 1:
      return None, None
    extra = None
    if cls.include_sentence_ends:
      for c in cls.sentence_ender:
        if word.endswith(c):
          extra = cls.sentence_end.word
          break
    if cls.include_phrase_ends:
      for c in cls.phrase_ender:
        if word.endswith(c):
          extra = cls.phrase_end.word
          break
    word = word.strip(cls.strip_chars)
    word = word.lower()
    if word.isalpha():
      return word, extra
    return None, None

  def pick_n_random(self, num_words, use_probabilities=True):
    # using the random word, print a list of the words that branch out from there and their probability
    rand_word_id = self.get_random_word()
    chosen_words = ''
    prior_word = 0
    prior_word_2 = 0
    nexts = {}
    for i in range(0, num_words):
      try:
        if rand_word_id == prior_word == prior_word_2: # break up chains of repeating words
          rand_word_id = self.get_random_word()
        rand_word = self.word_counts[rand_word_id].word
        chosen_words += rand_word + ' '
        prior_word_2 = prior_word
        prior_word = rand_word_id
        if rand_word_id not in self.next_words: # last word in text has no next
          rand_word_id = self.get_random_next(nexts, use_probabilities)
          continue
        nexts = self.next_words[rand_word_id]
        rand_word_id = self.get_random_next(nexts, use_probabilities)
        if not rand_word_id:
          rand_word_id = self.get_random_word()
      except Exception as ex:
        print "Exception: ", ex
        rand_word_id = self.get_random_word()
    print
    return chosen_words

  # def end_phrase(self, rand_word, chosen_words):
  #   if rand_word == None:
  #     return self.get_random_word()
  #   chosen_words.append(rand_word.w)
  #   elif rand_word == self.phrase_end:
  #     chosen_words.append(". ")

  def get_random_word(self):
    rand_word_id = self.nothing.id
    count = 0
    while rand_word_id == self.nothing.id:
      j = random.randint(0, len(self.word_counts) - 1)
      rand_word_id = self.word_counts.keys()[j]
      rand_word = self.word_counts[rand_word_id].word
      if self.blacklist and rand_word in self.blacklist:
        rand_word_id = self.nothing.id
      count += 1
      if count > 10:
        raise Exception("Need to add more text than that")
    return rand_word_id

  def get_random_next(self, nexts, use_probabilities):
    rand_word_id = self.nothing.id
    while rand_word_id == self.nothing.id:
      next_dist = []
      for next, count in nexts.items():
        if next is None:
          continue
        if use_probabilities:
          for j in range(0, count):
            next_dist.append(next)
        else:
          next_dist.extend(nexts) # todo: this is wrong
      if len(next_dist) < 1:
        return None
      k = random.randint(0, len(next_dist) - 1)
      rand_word_id = next_dist[k]
    return rand_word_id

  def get_nexts(self, word):
    id = word.__hash__()
    if id not in self.next_words:
      return [] # the last word in the text does not have nexts
    nexts = self.next_words[id]
    next_words = []
    for next in nexts:
      next_word = self.word_counts[next].word
      next_words.append(next_word)
    return sorted(next_words)

  def get_all_words(self):
    words = []
    for id, word in self.word_counts.items():
      words.append(word.word)
    return sorted(words)

# if __name__ == '__main__':
#   wg = WordToy(blacklist_txt, prose_txt)
#
#   if random_out:
#     num_words = random.randint(1, num_words)
#
#   result = wg.pick_n_random(num_words, use_probabilities)
#   print result

