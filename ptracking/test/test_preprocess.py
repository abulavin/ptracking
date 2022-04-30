import unittest
from ptracking.preprocess import *


class TestPreprocessing(unittest.TestCase):
    def test_combine(self):
        self.assertEqual(
            combine_petition_contents("Title one sentence",
                                      "Content one sentence."),
            "Title one sentence. Content one sentence.")

        self.assertEqual(
            combine_petition_contents("Title one sentence. Title two sentence",
                                      "Content one sentence."),
            "Title one sentence. Title two sentence. Content one sentence.")

        self.assertEqual(
            combine_petition_contents(
                "Title one sentence",
                "Content one sentence. Content two sentence."),
            "Title one sentence. Content one sentence. Content two sentence.")

        self.assertEqual(
            combine_petition_contents(
                "Title one sentence. Title two sentence",
                "Content one sentence. Content two sentence."),
            "Title one sentence. Title two sentence. Content one sentence. Content two sentence."
        )

    def test_tokenize_word(self):
        self.assertEqual(tokenize_words("i am good"), ['i', 'am', 'good'])

        self.assertEqual(tokenize_words("i  am good"), ['i', 'am', 'good'])

        self.assertEqual(tokenize_words("i   am good"), ['i', 'am', 'good'])

        self.assertEqual(tokenize_words("i'm good"), ['i', 'm', 'good'])

        self.assertEqual(tokenize_words("you're annoying..."),
                         ['you', 're', 'annoying'])

        self.assertEqual(tokenize_words("i hate eating/sleeping"),
                         ['i', 'hate', 'eating', 'sleeping'])

        self.assertEqual(tokenize_words("i know him(artemy)"),
                         ['i', 'know', 'him', 'artemy'])

    def test_remove_stopwords(self):
        self.assertEqual(remove_stopwords(['he', 'she', 'it']), [])
        self.assertEqual(
            remove_stopwords(
                ['i', 'love', 'eating', 'everyday', 'after', '10']),
            ['love', 'eating', 'everyday', '10'])
        self.assertEqual(
            remove_stopwords([
                'he', 'went', 'after', 'the', 'cat', 'at', '10', 'pm', 'when',
                'he', 'woke', 'up'
            ]), ['went', 'cat', '10', 'pm', 'woke'])

    def test_stem(self):
        self.assertEqual(
            stem([
                'do', 'you', 'really', 'think', 'it', 'is', 'weakness', 'that',
                'yields', 'to', 'temptation', 'i', 'tell', 'you', 'that',
                'there', 'are', 'terrible', 'temptations', 'which', 'it',
                'requires', 'strength', 'strength', 'and', 'courage', 'to',
                'yield', 'to'
            ]), [
                'do', 'you', 'realli', 'think', 'it', 'is', 'weak', 'that',
                'yield', 'to', 'temptat', 'i', 'tell', 'you', 'that', 'there',
                'are', 'terribl', 'temptat', 'which', 'it', 'requir',
                'strength', 'strength', 'and', 'courag', 'to', 'yield', 'to'
            ])

        self.assertEqual(
            stem([
                'what', 'have', 'you', 'been', 'doing', 'in', 'the', 'last',
                'week', 'my', 'friends', 'i', 'have', 'been', 'very', 'good',
                'thanks'
            ]), [
                'what', 'have', 'you', 'been', 'do', 'in', 'the', 'last',
                'week', 'my', 'friend', 'i', 'have', 'been', 'veri', 'good',
                'thank'
            ])

    def test_preprocessing(self):
        self.assertEqual(
            petition_preprocess(
                "This is an interesting title with one sentence",
                "This is an interesting content with one sentence"), [
                    'interest', 'title', 'one', 'sentence', 'interest',
                    'content', 'one', 'sentence'
                ])

        self.assertEqual(
            petition_preprocess("This line contains one question?",
                                "This line contains one answer!"), [
                                    'line', 'contain', 'one', 'question',
                                    'line', 'contain', 'one', 'answer'
                                ])

        self.assertEqual(
            petition_preprocess(
                "This title is very boring isn't it?  ",
                "There's one sentence. It's another paragraph here  "),
            ['title', 'bore', 'one', 'sentence', 'another', 'paragraph'])

    def test_short_word_removal(self):
        test_text = "text u 16"
        proccessed = petition_preprocess("", test_text)
        self.assertEqual(["text"], proccessed)
