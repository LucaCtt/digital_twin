from datetime import datetime
from enum import Enum
from fastapi import APIRouter, Query

from dt.api import schemas
from dt.data import DataRepository
from dt.energy import StateMatrix
from .. import errors


def get_consumption_router(repository: DataRepository, matrix: StateMatrix, tags: list[str | Enum]) -> APIRouter:
    router = APIRouter(tags=tags, prefix="/consumption")

    @router.get("/{when}")
    async def get_consumptions(when: datetime) -> schemas.ListResponse[schemas.ApplianceConsumption]:
        """Get the per-appliance consumption at a given date and time.
        """

        consumptions = matrix.consumptions(when)

        return schemas.ListResponse(value=[schemas.ApplianceConsumption(appliance_id=a.id, consumption=c) for a, c in consumptions.items()])

    @router.get("/total/{when}")
    async def get_consumption_total(when: datetime) -> schemas.ValueResponse[float]:
        """Get the total consumption at a given date and time.
        """

        return schemas.ValueResponse(value=matrix.total_consumption(when))

    @router.get("/total/")
    async def get_consumption_total_list(when: list[datetime] = Query()) -> schemas.ListResponse[float]:
        """Get the total consumption for the given dates and times.
        """

        return schemas.ListResponse(value=[matrix.total_consumption(w) for w in when])

    @router.get("/{appliance_id}/{when}")
    async def get_consumption_appliance(appliance_id: int, when: datetime) -> schemas.ValueResponse[float]:
        """Get the consumption of an appliance at a given date and time.
        """

        appliance = repository.get_appliance(appliance_id)

        if appliance is None:
            raise errors.APPLIANCE_NOT_FOUND

        return schemas.ValueResponse(value=matrix.appliance_consumption(appliance, when))

    return router
