"""Generated schema mirror.

DO NOT edit directly.
Authority: bonsai/idol-research/schema/discovery.py
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

IntentFamily = Literal["event", "music", "fan", "business", "growth", "risk"]
SourceKind = Literal["web", "news", "official", "sns", "music_platform", "ticket", "agency"]
DiscoveryKind = Literal["search_result", "mention", "track_signal", "business_signal"]

class CrawlIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    family: IntentFamily
    purpose: str
    template: str
    terms: list[str] = Field(default_factory=list)
    limit: int = Field(default=10, ge=1, le=100)
    enabled: bool = True

class CrawlParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    engine: Literal["bing", "google-news", "both"] = "both"
    user_agent: str
    intents: list[CrawlIntent]
    max_queries: int = Field(default=500, ge=1, le=5000)
    timeout_seconds: int = Field(default=20, ge=1, le=120)
    dedupe_key: Literal["url"] = "url"

class DiscoveryObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    observation_id: str
    observed_at: datetime
    family: IntentFamily
    intent: str
    kind: DiscoveryKind
    query: str
    title: str
    url: HttpUrl
    published_at: datetime | None = None
    source_name: str | None = None
    source_kind: SourceKind = "web"
    description: str | None = None
    discovery_engine: Literal["bing", "google-news"]
    subject: str | None = None
    subject_type: Literal["idol", "group", "song", "event", "venue", "agency", "brand", "unknown"] = "unknown"
    raw: dict = Field(default_factory=dict)
