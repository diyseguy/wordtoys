from word_toy import *
import unittest

class WordTests(unittest.TestCase):

    def test_parsing(self):
      words = ['it', 'is']
      wg = WordToy()
      wg._parse_words(words)
      wg._post_process_words()
      test = wg.pick_n_random(2)
      self.failUnless(test == 'it is ' or test == 'is it ')
      words.extend(['so','true'])
      wg = WordToy()
      wg._parse_words(words)
      wg._post_process_words()
      self.assertEqual(len(wg.word_counts),4)
      self.assertEqual(len(wg.next_words),3)

    def poe_small_array(self):
      # words = ''.join([line for line in self.poe_small_string().split('\n')]).split(' ')
      words2 = [word.split(' ') for word in [line for line in self.poe_small_string().split('\n')]]
      return words2

    def poe_small_string(self):
      text = """
         And all with pearl and ruby glowing
          Was the fair palace door,
         Through which came flowing, flowing, flowing,
          And sparkling ever more,
         A troop of Echoes, whose sweet duty
          Was but to sing,
         In voices of surpassing beauty,
          The wit and wisdom of their king.
      """
      return text

    def help_test_poe_small(self, wg):
      words = wg.pick_n_random(5)
      all_words = wg.get_all_words()
      self.assertEqual(len(all_words),37)
      and_nexts = wg.get_nexts('and')
      self.assertEqual(and_nexts, ['all','ruby','sparkling','wisdom'])
      self.assertEqual(wg.get_nexts('of'), ['echoes','surpassing','their'])
      self.assertEqual(wg.get_nexts('was'), ['but','the'])
      self.assertEqual(wg.get_nexts('flowing'),['flowing'])
      self.assertEqual(wg.get_nexts('beauty'), [])
      self.assertEqual(wg.get_nexts('.'), [])
      self.assertEqual(wg.get_nexts('palace'), ['door'])
      self.assertEqual(wg.get_nexts('door'), [])

    def test_load_words_from_file(self):
      wg = WordToy(black_list_file='blacklist.txt', prose_file='test1.txt')
      self.help_test_poe_small(wg)

    def test_load_words_from_string(self):
      prose_txt = self.poe_small_string()
      wg = WordToy(prose_txt=prose_txt)
      self.help_test_poe_small(wg)

    def test_load_words_from_array(self):
      lines = self.poe_small_array()
      wg = WordToy()
      for line in lines:
        wg._parse_words(line)
      wg._post_process_words()
      self.help_test_poe_small(wg)

    def test_big_file(self):
      wg = WordToy(black_list_file='blacklist.txt', prose_file='test_words.txt')
      words = wg.pick_n_random(5)
      all_words = wg.get_all_words()
      self.assertEqual(len(all_words),14330)
      purple_nexts = wg.get_nexts('purple')
      self.assertEqual(purple_nexts, ['. ', 'air', 'and', 'atmosphere', 'curtain', 'in', 'mountains', 'perfume', 'stem', 'to', 'violet', 'while'])
      vibrations_nexts = wg.get_nexts('vibrations')
      self.assertEqual(vibrations_nexts, ['generate', 'of', 'would'])
      self.assertEqual(wg.get_nexts('agitations'), [])


if __name__ == '__main__':
    unittest.main()

