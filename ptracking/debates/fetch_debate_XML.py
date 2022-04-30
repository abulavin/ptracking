import re
import xml.etree.ElementTree as ET
from urllib.request import urlopen

from bs4 import BeautifulSoup
from dateutil import parser
from ptracking.debates.fetch_debate_speeches import getSpeeches

page = urlopen("https://www.theyworkforyou.com/pwdata/scrapedxml/debates/")
hiperlink = "https://www.theyworkforyou.com/pwdata/scrapedxml/debates/"
soup = BeautifulSoup(page, features="lxml")
debates = soup.find_all('a')[6:]
debates = list(map(lambda x: x['href'],debates))

def getVignettesXML(date_start, date_end = None):
    start = parser.parse(date_start)  
    if date_end is not None:
        end = parser.parse(date_end)
    else:
        end = None
    speeches = list()

    for debate in debates:
        date = re.search("([0-9]{4}\-[0-9]{2}\-[0-9]{2})", debate).group(1)
        date = parser.parse(date)

        if end is not None:
            if start <= date and date <= end:
                xml = ET.parse(urlopen(hiperlink+debate))
                vignettes = getSpeeches(xml)
                speeches.extend(vignettes)
        else:  
            if start == date:
                xml = ET.parse(urlopen(hiperlink+debate))
                vignettes = getSpeeches(xml)
                speeches.extend(vignettes)

    return speeches
