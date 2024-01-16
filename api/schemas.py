"""Schemas for the API.

This module provides the schemas for the API. The schemas are used to validate
the data received from the API clients and to serialize the data returned by the API.

There is duplication the fields of the schemas and the model, but I don't know how to avoid that.
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel
from pydantic import BaseModel


class OperationModeBase(BaseModel):
    """The schema for an operation mode.
    """

    id: int
    name: str
    power_consumption: float
    default_duration: int | None = None

    # Enable creating an instance of this schema from a model.
    class Config:
        from_attributes = True


class ApplianceBase(BaseModel):
    """The schema for an appliance.
    """

    id: int
    device: str
    modes: list[OperationModeBase]

    # Enable creating an instance of this schema from a model.
    class Config:
        from_attributes = True


class RoutineActionBase(BaseModel):
    """The schema for a routine action.
    """

    id: int
    appliance: ApplianceBase
    mode: OperationModeBase
    duration: int | None = None

    # Enable creating an instance of this schema from a model.
    class Config:
        from_attributes = True


class RoutineBase(BaseModel):
    """The schema for a routine action.
    """

    id: int
    name: str
    when: datetime
    actions: list[RoutineActionBase]
    enabled: bool = True

    # Enable creating an instance of this schema from a model.
    class Config:
        from_attributes = True
