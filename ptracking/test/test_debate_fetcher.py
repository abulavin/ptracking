import unittest
import xml.etree.ElementTree as ET

from ptracking.debates.fetch_debate_speeches import *
from ptracking.debates.fetch_debate_XML import *
from ptracking.debates.insert_debate import *
from ptracking.test import TEST_RESOURCES

xml = ET.parse(TEST_RESOURCES.joinpath("speech.xml"))
speech = xml.find("speech")


class TestFetchDebates(unittest.TestCase):
    def test_getVignettesXML(self):
        self.assertEqual(getEid(speech), "2016-03-07b")

    def test_getText(self):
        self.assertEqual(getText(speech), (
            "I hope that hon. Members will be glad to hear that today we have published proposals for "
            "consultation to start the process of introducing a national funding formula for schools from 2017-18."
            " These plans will ensure that every school and local area, no matter where it is in the country, is funded"
            " fairly. It will ensure that pupils with similar needs attract the same level of funding and give "
            "headteachers far more certainty over future budgets. Areas with the highest need will attract the most funding,"
            " so pupils from disadvantaged backgrounds will continue to receive significant additional support. That is a key"
            " part of our core mission to have educational excellence everywhere."
        ))

    def test_getDate(self):
        self.assertEqual(getDate(speech), datetime(2016, 3, 7, 0, 0))

    def test_getSpeeches(self):
        speeches = getSpeeches(xml)
        self.assertEqual(len(speeches), 5)

    def test_getVignettesXMLOneDate(self):
        vignettes = getVignettesXML("1919-02-04")
        self.assertEqual(len(vignettes), 28)

    def test_getVignettesXMLBetweenDates(self):
        vignettes = getVignettesXML("1919-02-04", "1919-02-05")
        self.assertEqual(len(vignettes), 411)

    # def test_insertDebateBetweenDates(self):
    #     with cursor(Conns.SQLITE_MEMORY) as curr:
    #         insertDebate("1919-02-04",
    #                      "1919-02-05",
    #                      connection=Conns.SQLITE_MEMORY)
    #         curr.execute("SELECT * FROM VIGNETTE")
    #         count = curr.rowcount
    #         # There are 411 speeches during these dates in total
    #         self.assertEqual(count, 411)

    # def test_insertDebateOneDate(self):
    #     with cursor(Conns.SQLITE_MEMORY) as curr:
    #         # There are 28 speeches during these dates in total
    #         insertDebate("1919-02-04", connection=Conns.SQLITE_MEMORY)
    #         curr.execute("SELECT * FROM VIGNETTE")
    #         count = curr.rowcount
    #         self.assertEqual(count, 28)
