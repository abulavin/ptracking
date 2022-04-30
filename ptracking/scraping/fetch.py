import time
from dataclasses import asdict, astuple
from datetime import datetime
from typing import List

from ptracking.database import cursor, Petition, PetitionState, UPDATED_PETITION_ATTRS
import requests
from ptracking import config
from ptracking.scraping.debate import DebateFetcher
from ptracking.database.models import (UPDATED_PETITION_ATTRS, Petition,
                                       PetitionState)
from ptracking.scraping.petition import PetitionParser


def fetch_petitions(url):
    attempts = 0
    while attempts < 100:
        print("Fetching %s..." % url)
        try:
            response = requests.get(url, timeout=10)
        except Exception as e:
            print("Request failure: %s" % e)

        if response.ok:
            data = response.json()
            if "data" not in data:
                print(f"Empty data field for url {url}: {data}. Retrying")
                continue
            return data
        else:
            attempts += 1
            print("Fetch failed, retry %s" % attempts)
            time.sleep(5)


def parse_petitions(data) -> List[PetitionParser]:
    debate_fetcher = DebateFetcher(url=config['Sources']['debates'])
    return [PetitionParser(p, debate_fetcher) for p in data]


def insert_data(parsers: List[PetitionParser]):
    petitions = {}
    all_const_signatures = []
    all_country_signatures = []
    debates = {}

    for parser in parsers:
        petition = parser.petition
        constituency_signatures = parser.constituency_signatures
        country_signatures = parser.country_signatures
        debate = parser.debate

        # Multiple petitions sometimes refer to the same debate
        if debate is not None:
            debates[debate.debate_id] = debate

        # Somehow, the same petition ID may be returned more than once from the API
        if petition.petition_id not in petitions:
            petitions[petition.petition_id] = petition
            all_const_signatures += constituency_signatures
            all_country_signatures += country_signatures

    with cursor() as curr:
        for debate in debates.values():
            curr.execute(
                "INSERT INTO debate VALUES(%s, %s, %s) ON CONFLICT(debate_id) DO NOTHING",
                astuple(debate))
        for petition in petitions.values():
            print(f"Inserting petition ID: {petition.petition_id}")
            curr.execute(
                "SELECT updated_at, state FROM petition WHERE petition_id = %s",
                (petition.petition_id, ))
            result = curr.fetchone()
            if not result:
                curr.execute(
                    """INSERT INTO petition VALUES(
                    %(petition_id)s,
                    %(state)s,
                    %(title)s,
                    %(content)s,
                    %(processed_content)s,
                    %(created_at)s,
                    %(closed_at)s,
                    %(updated_at)s,
                    %(response_threshold)s,
                    %(debate_threshold)s,
                    %(moderation_threshold)s,
                    %(rejected_at)s,
                    %(rejected_reason)s,
                    %(signatures)s,
                    %(response_summary)s,
                    %(response_details)s,
                    %(debate_id)s,
                    %(topics)s
                )""", asdict(petition))
            elif needs_updating(*result, petition):
                attrs = {
                    k: v
                    for k, v in asdict(petition).items()
                    if k in UPDATED_PETITION_ATTRS
                }
                attrs['petition_id'] = petition.petition_id
                curr.execute(
                    """UPDATE petition SET
                            state = %(state)s,
                            closed_at = %(closed_at)s,
                            updated_at = %(updated_at)s,
                            response_threshold = %(response_threshold)s,
                            debate_threshold = %(debate_threshold)s,
                            moderation_threshold = %(moderation_threshold)s,
                            rejected_at = %(rejected_at)s,
                            rejected_reason = %(rejected_reason)s,
                            signatures = %(signatures)s,
                            response_summary = %(response_summary)s,
                            response_details = %(response_details)s,
                            debate_id = %(debate_id)s
                        WHERE petition_id = %(petition_id)s
                    """, attrs)
        for sign in constituency_signatures:
            curr.execute(
                """INSERT INTO signature_by_constituency VALUES(%s, %s, %s) 
                ON CONFLICT(petition_id, ons_id) UPDATE SET count = %s""",
                astuple(sign))
        for sign in country_signatures:
            curr.execute(
                """INSERT INTO signature_by_country VALUES(%s, %s, %s) 
                ON CONFLICT(petition_id, country) UPDATE SET count = %s""",
                astuple(sign))


def needs_updating(updated_at, state, petition: Petition) -> bool:
    return state == PetitionState.OPEN.value and updated_at < petition.updated_at


def already_scraped(url: str) -> bool:
    with cursor() as cur:
        cur.execute("SELECT 1 FROM scraped_url WHERE url = %s", (url, ))
        return cur.fetchone() is not None


def add_to_scraped(url: str):
    with cursor() as curr:
        curr.execute("INSERT INTO scraped_url VALUES(%s, %s)",
                     (url, datetime.now()))


def fetch():
    urls = {}
    for url in config['Sources']['open_petitions']:
        urls[url] = False
    for url in config['Sources']['other_petitions']:
        urls[url] = True

    for url, scrape_once in urls.items():
        print(f"Processing {url}")
        if scrape_once:
            if already_scraped(url):
                print("Already scraped, skipping")
                continue
            add_to_scraped(url)

        while url:
            data = fetch_petitions(url)
            parsers = parse_petitions(data['data'])
            insert_data(parsers)
            url = data["links"]["next"]
