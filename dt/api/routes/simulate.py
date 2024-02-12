from datetime import datetime
from enum import Enum
from fastapi import APIRouter, Query

from dt.api import schemas
from dt.data import DataRepository, Routine, RoutineAction, Appliance
from dt.energy import ConsumptionsMatrix, CostsMatrix, InconsistentRoutinesError, MaxPowerExceededError, RoutineOptimizer
from .. import errors


def get_simulate_router(repository: DataRepository, matrix: ConsumptionsMatrix, costs: CostsMatrix, tags: list[str | Enum]) -> APIRouter:
    router = APIRouter(tags=tags, prefix="/simulate")

    @router.post("")
    async def post_simulate(routine_in: schemas.RoutineIn) -> schemas.ListResponse[schemas.RecommendationOut]:
        """Simulates the addition of a routine.
        """
        error = None
        recommendations = []

        routine_model = __routine_schema_to_model(routine_in, repository)
        try:
            # Try to add the routine to the matrix to see if any conflicts are thrown
            matrix.add_routine(routine_model)
        except InconsistentRoutinesError as e:
            error = e

            for routine in e.routines:
                recommendation = schemas.RecommendationOut(type=schemas.RecommendationType.disable_routine,
                                                           context={"routine": schemas.RoutineOut.model_validate(routine)})
                recommendations.append(recommendation)

        except MaxPowerExceededError as e:
            error = e

            most_consuming = matrix.most_consuming_routines(e.when)
            recommendation = schemas.RecommendationOut(type=schemas.RecommendationType.disable_routine,
                                                       context={"routine": schemas.RoutineOut.model_validate(most_consuming[0])})
            recommendations.append(recommendation)

        # Try to find the best start time for the routine
        optimizer = RoutineOptimizer(matrix, costs)
        search_result = optimizer.find_best_start_time(routine_model)
        if search_result is not None:
            best_start_time, savings = search_result
            recommendation = schemas.RecommendationOut(type=schemas.RecommendationType.change_start_time,
                                                       context={"when": best_start_time, "savings": savings})
            recommendations.append(recommendation)

        return schemas.ListResponse(value=recommendations,
                                    error=schemas.ErrorOut(message=str(error),
                                                           context=__context_to_schemas(error.context)) if error else None)

    @router.post("/consumption/{when}")
    async def post_consumptions(routine_in: schemas.RoutineIn, when: datetime) -> schemas.ListResponse[schemas.ApplianceConsumption]:
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
    async def post_consumption_total_list(routine_in: schemas.RoutineIn, when: list[datetime] = Query()) -> schemas.ListResponse[float]:
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
    routine_dict["when"] = datetime.strptime(routine_dict["when"], "%H:%M")
    routine_dict["actions"] = actions
    return Routine(**routine_dict)


def __context_to_schemas(context: dict) -> dict:
    """Converts a context dictionary to a dictionary of schemas.

    Args:
        context (dict): The context dictionary.

    Returns:
        dict: The dictionary of schemas.
    """

    for key, value in context.items():
        if type(value) is Routine:
            context[key] = schemas.RoutineOut.model_validate(value)
        if type(value) is list:
            context[key] = [schemas.RoutineOut.model_validate(r) for r in value] 
        if type(value) is RoutineAction:
            context[key] = schemas.RoutineActionOut.model_validate(value)
        if type(value) is Appliance:
            context[key] = schemas.ApplianceOut.model_validate(value)

    return context
