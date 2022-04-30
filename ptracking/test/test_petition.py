import json
import os
from dataclasses import dataclass
from unittest import TestCase

from ptracking.database import (ConstituencySignatures, CountrySignatures,
                                Debate, Petition)
from ptracking.scraping.petition import parse_date
from ptracking.scraping.petition import PetitionParser
from ptracking.test import TEST_RESOURCES

# The open petition has a debate field
TEST_PETITIONS = {
    "open": "open_petition.json",
    "closed": "closed_petition.json",
    "rejected": "rejected_petition.json"
}


@dataclass
class TestData:
    parser: PetitionParser
    data: dict


class PetitionTest(TestCase):
    # Create dummy fetcher to use for dependency injection
    # when testing the parser. We shouldn't really be inspecting
    # methods like this but we want to double check that the url
    # is given the right debate id.
    class DummyDebateFetcher:
        passed_debate = ""

        def fetch_debate_text(self, debate_id: str) -> str:
            self.__class__.passed_debate = debate_id
            return "Valid text"

    @classmethod
    def setUpClass(cls) -> None:
        cls.fetcher = cls.DummyDebateFetcher()
        cls.open = cls.load_test_json(TEST_PETITIONS['open'])
        cls.closed = cls.load_test_json(TEST_PETITIONS['closed'])
        cls.rejected = cls.load_test_json(TEST_PETITIONS['rejected'])

    @classmethod
    def load_test_json(cls, filename: str) -> TestData:
        with open(os.path.join(TEST_RESOURCES, filename), "rb") as fp:
            data = json.load(fp)['data']
        return TestData(PetitionParser(data, cls.fetcher), data)

    def test_loads_id_correctly(self):
        self.assertEqual(self.open.parser.id, self.open.data['id'])
        self.assertEqual(self.closed.parser.id, self.closed.data['id'])
        self.assertEqual(self.rejected.parser.id, self.rejected.data['id'])

    # def test_attributes_of_correct_type(self):
    #     for parser in [
    #             self.open.parser, self.closed.parser, self.rejected.parser
    #     ]:
    #         parser = self.open.parser
    #         petition = parser.petition
    #         debate = parser.debate
    #         const_sings = parser.constituency_signatures
    #         country_signs = parser.country_signatures

    #         self.assertIsInstance(petition, Petition)
    #         self.assertIsInstance(debate, Debate)
    #         self.assertIsInstance(const_sings, list)
    #         self.assertTrue(
    #             all(type(s) is ConstituencySignatures for s in const_sings))
    #         self.assertIsInstance(country_signs, list)
    #         self.assertTrue(
    #             all(type(s) is CountrySignatures for s in country_signs))

    # def test_parses_open_petition(self):
    #     self.check_attributes_match(self.open)

    #     petition = self.open.parser.petition
    #     # This is an open petition that has not been responded to yet
    #     self.assertIsNone(petition.response_summary)
    #     self.assertIsNone(petition.response_details)
    #     self.assertIsNone(petition.rejected_at)

    def check_attributes_match(self, test_data: TestData):
        petition = test_data.parser.petition
        data = test_data.data
        attrs = data['attributes']
        # There's probably a nicer way of doing this where we iterate over
        # Petition.__dataclass_fields__ but now I am seeing the mistake
        # of naming Petition fields more concisely than what they're given
        # in the json...
        self.assertEqual(petition.petition_id, data['id'])
        self.assertEqual(petition.state, attrs['state'])
        self.assertIn(petition.title, attrs['action'])
        self.assertIn(attrs["background"], petition.content)
        self.assertIn(attrs["additional_details"], petition.content)
        self.assertEqual(petition.created_at, parse_date(attrs['created_at']))
        self.assertEqual(petition.updated_at, parse_date(attrs['updated_at']))
        self.assertEqual(petition.moderation_threshold,
                         parse_date(attrs['moderation_threshold_reached_at']))
        self.assertEqual(petition.signatures, attrs['signature_count'])

    # def test_parses_debate_correctly(self):
    #     parser = self.open.parser
    #     petition = parser.petition
    #     debate = parser.debate
    #     # Check the debate id is what was passed to the fetcher.
    #     self.assertEqual(petition.debate_id, debate.debate_id)
    #     self.assertEqual(petition.debate_id, self.fetcher.passed_debate)

    def test_throws_on_bad_data(self):
        # PetitionParser should throw if the data it gets its not 'dict-like'
        data = object()
        with self.assertRaises(ValueError):
            PetitionParser(data, self.fetcher)

        with self.assertRaises(KeyError):
            PetitionParser({"missing": "keys"}, self.fetcher)

        with self.assertRaises(KeyError):
            PetitionParser({"attributes": {}, "id": 1}, self.fetcher)

    # def test_parses_closed_petition(self):
    #     self.check_attributes_match(self.closed)

    # def test_parses_rejected_petition(self):
    #     test_data = self.rejected
    #     self.check_attributes_match(test_data)
    #     petition = test_data.parser.petition
    #     attrs = test_data.data['attributes']
    #     self.assertEqual(petition.rejected_at,
    #                      parse_date(attrs['rejected_at']))
    #     self.assertEqual(petition.rejected_reason, attrs['rejection']['code'])
