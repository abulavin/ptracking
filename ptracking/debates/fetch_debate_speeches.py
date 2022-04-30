from ptracking.database import Vignette
from datetime import datetime

def parse_day(datestr: str) -> datetime:
    if not datestr:
        return datestr
    return datetime.strptime(datestr, "%Y-%m-%d")

def getEid(node):
    return node.attrib['id'].split('/')[2][0:11]

def getDate(node):
    if 'id' in node.attrib:
        date = node.attrib['id'].split('/')[2][0:10]
        return parse_day(date)
    else:
        return None

def getText(node):
    texts = []
    for p in node.findall('p'):
        text = "".join(p.itertext())
        if text != None and len(text) > 0:
            texts.append(text)
    return (' '.join(texts))


def getSpeeches(XML):
    vignettes = list()
    speech_order = 1
    for speech in XML.findall("speech"):
        debate_id = getEid(speech)
        content = getText(speech)
        date = getDate(speech)
        vignettes.append(Vignette(debate_id, content, speech_order, date))
        speech_order += 1
    return vignettes
