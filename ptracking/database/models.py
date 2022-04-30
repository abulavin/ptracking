from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

class PetitionState(Enum):
    REJECTED = "rejected"
    OPEN = "open"
    CLOSED = "closed"


UPDATED_PETITION_ATTRS = [
    "state",
    "closed_at",
    "updated_at",
    "response_threshold",
    "debate_threshold",
    "moderation_threshold",
    "rejected_at",
    "rejected_reason",
    "signatures",
    "response_summary",
    "response_details",
    "debate_id",
]


@dataclass
class Petition:
    petition_id: int
    title: str
    content: str
    created_at: datetime
    closed_at: datetime
    signatures: int
    processed_content: List[str]
    debate_at: datetime
    response_at: datetime
    debate_threshold: datetime
    response_threshold: datetime


@dataclass
class ConstituencySignatures:
    petition_id: int
    ons_code: str
    count: int


@dataclass
class CountrySignatures:
    petition_id: int
    country: str
    count: int


@dataclass
class Debate:
    debate_id: str
    title: str
    debate_date: datetime

@dataclass
class Vignette:
    debate_id: str
    content: str
    p_order: int
    date: datetime

@dataclass
class Tweet:
    tweet_id: int
    petition_id: int
    user_id: int
    verified: bool
    user_followers: int
    user_friends: int
    created_at: datetime
    likes: int
    retweets: int
    replies: int
