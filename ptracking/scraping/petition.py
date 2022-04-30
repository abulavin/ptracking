from datetime import datetime
import re
from functools import cached_property
from typing import Iterable, List, Tuple, Union

from ptracking.preprocess.preprocess import petition_preprocess
from ptracking.scraping.debate import DebateFetcher
from ptracking.database import (ConstituencySignatures, CountrySignatures,
                                Debate, Petition)

__all__ = ["PetitionParser"]


def parse_date(datestr: str) -> datetime:
    if not datestr:
        return datestr
    return datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S.%fZ")


class PetitionParser:
    required_keys = [
        "id",
        "attributes",
    ]
    required_attrs = [
        "state", "action", "background", "additional_details", "created_at",
        "closed_at", "updated_at", "response_threshold_reached_at",
        "debate_threshold_reached_at", "moderation_threshold_reached_at",
        "rejected_at", "rejection", "signature_count", "government_response",
        "debate"
    ]

    def __init__(self, data: dict, debate_fetcher: DebateFetcher) -> None:
        self.json = data
        if not hasattr(data, "__getitem__"):
            raise ValueError(f"data in constructor invalid type: {type(data)}")
        if fields := self._missing_fields(data):
            raise KeyError(
                f"Petition JSON missing the following fields: {','.join(fields)}"
            )
        if fields := self._missing_attrs(data['attributes']):
            raise KeyError(
                f"Petition {data['id']} attributes missing the following fields: {','.join(fields)}"
            )

        self.id: int = data['id']
        self._attrs: dict = data['attributes']
        self._debate_fetcher = debate_fetcher

    def _missing_fields(self, data: dict) -> List[str]:
        return [
            field for field in PetitionParser.required_keys
            if field not in data
        ]

    def _missing_attrs(self, data: dict) -> List[str]:
        return [
            atr for atr in PetitionParser.required_attrs if atr not in data
        ]

    @cached_property
    def petition(self) -> Petition:
        # Additional details not always provided.
        title = self._strip_chars(self._attrs['action'])
        content = self._parse_content()
        rejection = self._parse_rejection()
        summary, details = self._parse_response()
        debate = self.debate
        debate_id = None if debate is None else debate.debate_id
        return Petition(petition_id=self.id,
                        state=self._attrs['state'],
                        title=title,
                        content=content,
                        processed_content=petition_preprocess(title, content),
                        created_at=parse_date(self._attrs['created_at']),
                        closed_at=parse_date(self._attrs['closed_at']),
                        updated_at=parse_date(self._attrs['updated_at']),
                        response_threshold=parse_date(
                            self._attrs['response_threshold_reached_at']),
                        debate_threshold=parse_date(
                            self._attrs['debate_threshold_reached_at']),
                        moderation_threshold=parse_date(
                            self._attrs['moderation_threshold_reached_at']),
                        rejected_at=parse_date(self._attrs['rejected_at']),
                        rejected_reason=rejection,
                        signatures=int(self._attrs['signature_count']),
                        response_summary=summary,
                        response_details=details,
                        debate_id=debate_id,
                        topics=[])

    def _parse_content(self) -> str:
        def convert_none_to_str(x):
            return "" if x is None else x

        # Sometimes these fields may be set to null, as opposed to be just missing
        background = convert_none_to_str(self._attrs.get('background', ''))
        details = convert_none_to_str(self._attrs.get('additional_details',
                                                      ''))
        return self._strip_chars(background + " " + details)

    def _parse_rejection(self) -> Union[str, None]:
        reason = self._attrs['rejection']
        if not reason:
            return None
        return reason['code']

    def _parse_response(self) -> Tuple[Union[str, None], Union[str, None]]:
        if resp := self._attrs['government_response']:
            summary = self._strip_chars(resp['summary'])
            details = self._strip_chars(resp['details'])
            return summary, details
        return (None, None)

    def _strip_chars(self, content: str) -> str:
        return content.replace("\n", "").replace("\r", "")

    def _parse_debate_id(self) -> Union[str, None]:
        if debate := self._attrs['debate']:
            if url := debate['transcript_url']:
                regex = r"https:\/\/hansard\.parliament\.uk\/[aA-zZ]+\/\d{4}-\d\d-\d\d\/debates\/(?P<id>([A-Z]|[0-9]|-)*)\/[aA-zZ]+"
                m = re.search(regex, url)
                if m:
                    return m.group("id")
        return None

    @cached_property
    def debate(self) -> Union[Debate, None]:
        debate_id = self._parse_debate_id()
        if debate_id is None:
            return None

        text = self._debate_fetcher.fetch_debate_text(debate_id)
        if text is None:
            return None

        return Debate(debate_id=debate_id,
                      title=text.title,
                      debate_date=self._attrs['debate'].get('debated_on'))

    @cached_property
    def constituency_signatures(self) -> List[ConstituencySignatures]:
        signatures = self._attrs.get('signatures_by_constituency')
        return self._parse_signatures(
            lambda s: ConstituencySignatures(
                self.id, ons_code=s['ons_code'], count=s['signature_count']),
            signatures)

    @cached_property
    def country_signatures(self) -> List[CountrySignatures]:
        signatures = self._attrs.get('signatures_by_country')
        return self._parse_signatures(
            lambda s: CountrySignatures(petition_id=self.id,
                                        country=s['name'],
                                        count=s['signature_count']),
            signatures)

    def _parse_signatures(self, map_func, signatures: Iterable) -> List:
        if signatures is None:
            return []
        if not hasattr(signatures, "__iter__"):
            raise ValueError(
                f"object containing petition signatures not iterable. Type: {type(signatures)}"
            )
        return list(map(map_func, signatures))
