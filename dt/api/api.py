"""API module for the Digital Twin.

This module provides the REST API for the Digital Twin, implemented using [FastAPI](https://fastapi.tiangolo.com/).
"""

from datetime import datetime
from fastapi import FastAPI
import fastapi
from fastapi.responses import JSONResponse

from data import DataRepository, Routine, RoutineAction
from dt.config import EnergyConfig
from energy import ConflictError, ConsumptionsMatrix, Recommendation, RoutineSimulator, CostsMatrix
from . import errors
from .schemas import ApplianceOut, RecommendationOut, RoutineOut, RoutineIn

__CONSUMPTION_TAG = "Consumption"
__APPLIANCE_TAG = "Appliance"
__ROUTINE_TAG = "Routine"
__SIMULATE_TAG = "Simulation"


def create_api(repository: DataRepository, config: EnergyConfig, title="Digital Twin API", version: str = "1.0.0") -> FastAPI:
    """Create a FastAPI instance.

    Create a new FastAPI instance, using the given data repository and
    consumptions matrix. These are not passed to routes using dependency injection
    as they are global to the application.

    Args:
        repository (DataRepository): The data repository.
        title (str, optional): The API title. Defaults to "Digital Twin API".
        version (str, optional): The API version. Defaults to "1.0.0". Remember to update this value when you make changes to the API.
        Please follow the [Semantic Versioning](https://semver.org/) guidelines.

    Returns:
        FastAPI: The FastAPI instance.
    """
    matrix = ConsumptionsMatrix(
        repository.get_appliances(), repository.get_routines(), config)
    costs = CostsMatrix(config)

    api = FastAPI(
        title=title,
        version=version,
        docs_url="/",
        redoc_url=None
    )

    @api.exception_handler(ConflictError)
    async def conflict_error_handler(request: fastapi.Request, exc: ConflictError):
        recommendations = [
            r.message for r in exc.recommendations] if exc.recommendations else None
        return JSONResponse(status_code=409, content={"error": str(exc), "recommendations": recommendations})

    @api.post("/simulate", tags=[__SIMULATE_TAG])
    async def post_simulate(routine_in: RoutineIn) -> list[RecommendationOut]:
        """Simulates the addition of a routine.

        **Args**:
        - `routine_in (RoutineIn)`: The routine to simulate.

        **Returns**:
        - `list[RecommendationOut]`: A list of recommendations about the routine.
        """

        simulator = RoutineSimulator(matrix, costs, config.max_power)
        recommendation = simulator.simulate(
            __routine_schema_to_model(routine_in, repository))
        return [__recommendation_model_to_schema(r) for r in recommendation]

    @api.post("/simulate/consumption/{when}", tags=[__SIMULATE_TAG])
    async def post_simulate_consumption_total(routine_in: RoutineIn, when: datetime) -> float:
        """Simulates the addition of a routine and returns the total consumption at a given date and time.

        **Args**:
        - `routine_in (RoutineIn)`: The routine to simulate.
        - `when (datetime)`: The date and time.

        **Returns**:
        - `float`: The total consumption at the given date and time, in watts.
        """

        simulator = RoutineSimulator(matrix, costs, config.max_power)
        simulator.simulate(__routine_schema_to_model(routine_in, repository))
        return simulator.simulated_consumption_matrix.total_consumption(when)

    @api.post("/consumption/{appliance_id}/{when}", tags=[__SIMULATE_TAG])
    async def post_simulate_consumption_appliance(routine_in: RoutineIn, appliance_id: int, when: datetime) -> float:
        """Simulates the addition of a routine and returns the consumption of an appliance at a given date and time.

        **Args**:
        - `routine_in (RoutineIn)`: The routine to simulate.
        - `appliance_id (int)`: The appliance ID.
        - `when (datetime)`: The date and time.

        **Returns**:
        - `float`: The consumption of the appliance at the given date and time, in watts.
        """

        appliance = repository.get_appliance(appliance_id)

        if appliance is None:
            raise errors.APPLIANCE_NOT_FOUND

        simulator = RoutineSimulator(matrix, costs, config.max_power)
        simulator.simulate(__routine_schema_to_model(routine_in, repository))
        return simulator.simulated_consumption_matrix.consumption(appliance, when)

    @api.get("/consumption/{when}", tags=[__CONSUMPTION_TAG])
    async def get_consumption_total(when: datetime) -> float:
        """Get the total consumption at a given date and time.

        **Args**:
        - `when (datetime)`: The date and time.

        **Returns**:
        - `float`: The total consumption at the given date and time, in watts.
        """

        return matrix.total_consumption(when)

    @api.get("/consumption/{appliance_id}/{when}", tags=[__CONSUMPTION_TAG])
    async def get_consumption_appliance(appliance_id: int, when: datetime) -> float:
        """Get the consumption of an appliance at a given date and time.

        **Args**:
        - `appliance_id (int)`: The appliance ID.
        - `when (datetime)`: The date and time.

        **Returns**:
        - `float`: The consumption of the appliance at the given date and time, in watts.
        """

        appliance = repository.get_appliance(appliance_id)

        if appliance is None:
            raise errors.APPLIANCE_NOT_FOUND

        return matrix.consumption(appliance, when)

    @api.get("/appliance/{appliance_id}", tags=[__APPLIANCE_TAG])
    async def get_appliance(appliance_id: int) -> ApplianceOut:
        """Get an appliance by ID.

        **Args**:
        - `appliance_id (int)`: The appliance ID.

        **Returns**:
        - `ApplianceOut`: The appliance.
        """

        appliance = repository.get_appliance(appliance_id)

        if appliance is None:
            raise errors.APPLIANCE_NOT_FOUND

        return ApplianceOut.model_validate(appliance)

    @api.get("/appliance", tags=[__APPLIANCE_TAG])
    async def get_appliances() -> list[ApplianceOut]:
        """Get all appliances.

        **Returns**:
        - `list[ApplianceOut]`: The appliances.
        """

        return [ApplianceOut.model_validate(a) for a in repository.get_appliances()]

    @api.get("/routine/{routine_id}", tags=[__ROUTINE_TAG])
    async def get_routine(routine_id: int) -> RoutineOut:
        """Get a routine by ID.

        **Args**:
        - `routine_id (int)`: The routine ID.

        **Returns**:
        - `RoutineOut`: The routine.
        """

        routine = repository.get_routine(routine_id)

        if routine is None:
            raise errors.ROUTINE_NOT_FOUND

        return RoutineOut.model_validate(routine)

    @api.get("/routine", tags=[__ROUTINE_TAG])
    async def get_routines() -> list[RoutineOut]:
        """Get all routines.

        **Returns**:
        - `list[RoutineOut]`: The routines.
        """

        return [RoutineOut.model_validate(r) for r in repository.get_routines()]

    return api


def __routine_schema_to_model(routine_in: RoutineIn, repository: DataRepository) -> Routine:
    actions = []

    for action_in in routine_in.actions:
        appliance = repository.get_appliance(action_in.appliance_id)
        if appliance is None:
            raise errors.APPLIANCE_INVALID

        mode = appliance.get_mode(action_in.mode_id)
        if mode is None:
            raise errors.APPLIANCE_INVALID

        action_dict = vars(action_in)
        action_dict["appliance"] = appliance
        action_dict["mode"] = mode

        actions.append(RoutineAction(**action_dict))

    routine_dict = vars(routine_in)
    routine_dict["actions"] = actions
    return Routine(**routine_dict)


def __recommendation_model_to_schema(recommendation: Recommendation) -> RecommendationOut:
    return RecommendationOut(**vars(recommendation))
