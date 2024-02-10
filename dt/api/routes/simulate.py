from datetime import datetime
from enum import Enum
from fastapi import APIRouter, Query

from api import schemas
from dt.api.schemas import RoutineIn
from .. import errors
from data import DataRepository, Routine, RoutineAction
from energy import ConsumptionsMatrix, CostsMatrix, RoutineOptimizer


def get_simulate_router(repository: DataRepository, matrix: ConsumptionsMatrix, costs: CostsMatrix, tags: list[str | Enum]) -> APIRouter:
    router = APIRouter(tags=tags, prefix="/simulate")

    @router.post("/")
    async def post_simulate(routine_in: schemas.RoutineIn) -> schemas.BaseResponse:
        """Simulates the addition of a routine.
        """

        routine_model = __routine_schema_to_model(routine_in, repository)
        # Try to add the routine to the matrix to see if any conflicts are thrown
        matrix.add_routine(routine_model)

        # If there are no conflicts, try to find the best start time for the routine
        optimizer = RoutineOptimizer(matrix, costs)
        recommendation = optimizer.find_best_start_time(routine_model)

        return schemas.BaseResponse(recommendations=[schemas.RecommendationOut.model_validate(recommendation)])

    @router.post("/consumption/{when}")
    async def post_consumptions(routine_in: RoutineIn, when: datetime) -> schemas.ListResponse[schemas.ApplianceConsumption]:
        """Get the per-appliance consumption at a given date and time.
        """

        simulated = matrix.add_routine(
            __routine_schema_to_model(routine_in, repository))
        consumptions = simulated.consumptions(when)

        return schemas.ListResponse(value=[schemas.ApplianceConsumption(appliance_id=a.id, consumption=c) for a, c in consumptions.items()])

    @router.post("/consumption/total/{when}")
    async def post_simulate_consumption_total(routine_in: schemas.RoutineIn, when: datetime) -> schemas.ValueResponse[float]:
        """Simulates the addition of a routine and returns the total consumption at a given date and time.
        """

        simulated = matrix.add_routine(
            __routine_schema_to_model(routine_in, repository))
        return schemas.ValueResponse(value=simulated.total_consumption(when))

    @router.post("/consumption/total/")
    async def post_consumption_total_list(routine_in: RoutineIn, when: list[datetime] = Query()) -> schemas.ListResponse[float]:
        """Get the total consumption for the given dates and times.
        """

        simulated = matrix.add_routine(
            __routine_schema_to_model(routine_in, repository))
        return schemas.ListResponse(value=[simulated.total_consumption(w) for w in when])

    @router.post("/consumption/{appliance_id}/{when}")
    async def post_simulate_consumption_appliance(routine_in: schemas.RoutineIn, appliance_id: int, when: datetime) -> schemas.ValueResponse[float]:
        """Get the consumption of an appliance at a given date and time.
        """
        appliance = repository.get_appliance(appliance_id)

        if appliance is None:
            raise errors.APPLIANCE_NOT_FOUND

        simulated = matrix.add_routine(
            __routine_schema_to_model(routine_in, repository))
        return schemas.ValueResponse(value=simulated.appliance_consumption(appliance, when))

    return router


def __routine_schema_to_model(routine_in: schemas.RoutineIn, repository: DataRepository) -> Routine:
    """Convert a routine schema to a routine model.

    Args:
        routine_in (schemas.RoutineIn): The routine schema.
        repository (DataRepository): The data repository to get the routine model from.

    Raises:
        errors.APPLIANCE_INVALID: Appliance or a mode of the appliance not found in the repository.

    Returns:
        Routine: _description_
    """

    actions = []

    for action_in in routine_in.actions:
        appliance = repository.get_appliance(action_in.appliance_id)
        if appliance is None:
            raise errors.APPLIANCE_INVALID

        mode = appliance.get_mode(action_in.mode_id)
        if mode is None:
            raise errors.APPLIANCE_INVALID

        action_dict = vars(action_in).copy()
        action_dict["appliance"] = appliance
        action_dict["mode"] = mode
        action_dict["duration"] = action_dict["duration"] // 60
        action_dict.pop("appliance_id")
        action_dict.pop("mode_id")

        actions.append(RoutineAction(**action_dict))

    routine_dict = vars(routine_in)
    routine_dict["actions"] = actions
    return Routine(**routine_dict)
