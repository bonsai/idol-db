"""Canonical idol-data schema.

Pydantic is the source of truth. JSON Schema / JSONL are generated artifacts.
LangChain consumes these models for structured output; LangGraph orchestrates
observation -> normalization -> validation; LangSmith traces and evaluates
the pipeline.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, HttpUrl


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: str
    source_url: HttpUrl | None = None
    publisher: str | None = None
    accessed_at: datetime | None = None
    retrieved_at: datetime | None = None
    confidence: Literal["low", "medium", "high"] = "medium"


class Idol(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    type: Literal["person", "idol"] = "idol"
    label: str
    label_reading: str | None = None
    aliases: list[str] = []
    groups: list[str] = []
    agency: str | None = None
    region: str | None = None
    tags: list[str] = []
    roles: list[str] = []
    activities: list[dict[str, Any]] = []
    active_period: dict[str, str | None] | None = None
    sources: list[Provenance] = []
    provenance: Provenance | None = None


class Group(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    type: Literal["group"] = "group"
    label: str
    aliases: list[str] = []
    agency: str | None = None
    region: str | None = None
    tags: list[str] = []
    members: list[str] = []
    sources: list[Provenance] = []


class Venue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    type: Literal["venue"] = "venue"
    label: str
    region: str | None = None
    address: str | None = None
    sources: list[Provenance] = []


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str
    type: Literal["event"] = "event"
    name: str
    date: str
    venue: str | None = None
    region: str | None = None
    category: str | None = None
    performers: list[str] = []
    source_url: HttpUrl | None = None
    accessed_at: datetime | None = None
    admission: dict[str, Any] | None = None


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    observation_id: str | None = None
    observed_at: datetime
    entity_type: str
    entity_id: str
    source: Provenance
    facts: dict[str, Any] = {}
    raw: dict[str, Any] | None = None


class Hypothesis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    hypothesis_id: str
    statement: str
    target_ids: list[str] = []
    evidence_observation_ids: list[str] = []
    status: Literal["open", "supported", "rejected", "uncertain"] = "open"
    created_at: datetime
    updated_at: datetime | None = None


class Feature(BaseModel):
    model_config = ConfigDict(extra="forbid")
    feature_id: str
    entity_id: str
    name: str
    value: float | str | bool | list[str] | None = None
    generated_at: datetime
    source_observation_ids: list[str] = []


class Recommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    recommendation_id: str
    entity_id: str
    score: float
    reasons: list[str] = []
    generated_at: datetime
    model_version: str


CanonicalRecord = Idol | Group | Venue | Event | Observation | Hypothesis | Feature | Recommendation
