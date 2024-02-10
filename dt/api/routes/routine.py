from enum import Enum
from fastapi import APIRouter

from dt.api import schemas
from dt.data import DataRepository
from .. import errors


def get_routine_router(repository: DataRepository, tags: list[str | Enum]) -> APIRouter:
    router = APIRouter(tags=tags, prefix="/routine")

    @router.get("/{routine_id}")
    async def get_routine(routine_id: int) -> schemas.ValueResponse[schemas.RoutineOut]:
        """Get a routine by ID.
        """

        routine = repository.get_routine(routine_id)

        if routine is None:
            raise errors.ROUTINE_NOT_FOUND

        return schemas.ValueResponse(value=schemas.RoutineOut.model_validate(routine))

    @router.get("/")
    async def get_routines() -> schemas.ListResponse[schemas.RoutineOut]:
        """Get all routines.
        """

        return schemas.ListResponse(value=[schemas.RoutineOut.model_validate(r) for r in repository.get_routines()])

    return router
