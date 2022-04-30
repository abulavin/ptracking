from ptracking.database.database import cursor
from ptracking.debates.fetch_debate_XML import getVignettesXML


def insertDebate(date_start, date_end=None):
    with cursor() as curr:
        speeches = getVignettesXML(date_start, date_end)
        for vignette in speeches:
            curr.execute(
                "INSERT INTO debate (debate_id, content, p_id, date) values (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (vignette.debate_id, vignette.content,
                 vignette.p_order, vignette.date))

def runDebateFetcher():
    insertDebate("2010-01-01","2022-01-01")