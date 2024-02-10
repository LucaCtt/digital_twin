from enum import Enum
from fastapi import APIRouter

from api import schemas
from .. import errors
from data import DataRepository


def get_appliance_router(repository: DataRepository, tags: list[str | Enum]) -> APIRouter:
    router = APIRouter(tags=tags, prefix="/appliance")

    @router.get("/{appliance_id}")
    async def get_appliance(appliance_id: int) -> schemas.ValueResponse[schemas.ApplianceOut]:
        """Get an appliance by ID.
        """

        appliance = repository.get_appliance(appliance_id)

        if appliance is None:
            raise errors.APPLIANCE_NOT_FOUND

        return schemas.ValueResponse(value=schemas.ApplianceOut.model_validate(appliance))

    @router.get("/")
    async def get_appliances() -> schemas.ListResponse[schemas.ApplianceOut]:
        """Get all appliances.
        """

        return schemas.ListResponse(value=[schemas.ApplianceOut.model_validate(a) for a in repository.get_appliances()])

    return router
