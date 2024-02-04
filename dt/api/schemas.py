"""Schemas for the API.

This module provides the schemas for the API. The schemas are used to validate
the data received from the API clients and to serialize the data returned by the API.

There is duplication the fields of the schemas and the model, but I don't know how to avoid that.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar
from pydantic import BaseModel
from pydantic import BaseModel


class OperationModeOut(BaseModel):
    """The schema for an operation mode.
    """

    id: int
    name: str
    power_consumption: float
    default_duration: int | None = None

    # Enable creating an instance of this schema from a model.
    class Config:
        from_attributes = True


class ApplianceOut(BaseModel):
    """The schema for an appliance.
    """

    id: int
    device: str
    modes: list[OperationModeOut]

    # Enable creating an instance of this schema from a model.
    class Config:
        from_attributes = True


class RoutineActionOut(BaseModel):
    """The schema for a routine action.
    """

    id: int
    appliance: ApplianceOut
    mode: OperationModeOut
    duration: int | None = None

    # Enable creating an instance of this schema from a model.
    class Config:
        from_attributes = True


class RoutineOut(BaseModel):
    """The schema for a routine action.
    """

    id: int
    name: str
    when: datetime
    actions: list[RoutineActionOut]
    enabled: bool = True

    # Enable creating an instance of this schema from a model.
    class Config:
        from_attributes = True


class RoutineActionIn(BaseModel):
    """The schema for an input routine action.
    """

    id: int
    appliance_id: int
    mode_id: int
    duration: int | None = None


class RoutineIn(BaseModel):
    """The schema for an input routine.
    """

    name: str
    when: datetime
    actions: list[RoutineActionIn]
    enabled: bool = True


class RecommendationOut(BaseModel):
    message: str
    context: dict[str, Any] | None = None

    # Enable creating an instance of this schema from a model.
    class Config:
        from_attributes = True

class ErrorOut(BaseModel):
    message: str
    context: dict[str, Any] | None = None


class BaseResponse(BaseModel):
    error: ErrorOut | None = None
    recommendations: list[RecommendationOut] | None = None

T = TypeVar("T")

class ValueResponse(BaseResponse, Generic[T]):
    value: T

class ListResponse(BaseResponse, Generic[T]):
    value: list[T]