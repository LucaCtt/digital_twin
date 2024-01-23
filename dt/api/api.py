"""API module for the Digital Twin.

This module provides the REST API for the Digital Twin, implemented using [FastAPI](https://fastapi.tiangolo.com/).
"""

from datetime import datetime
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from data import DataRepository, Routine, RoutineAction
from consumptions import ConsumptionsMatrix
from . import errors
from .schemas import ApplianceOut, RoutineOut, RoutineIn

__CONSUMPTION_TAG = "Consumption"
__APPLIANCE_TAG = "Appliance"
__ROUTINE_TAG = "Routine"


def create_api(repository: DataRepository, serve_static=False, serve_dir="static", title="Digital Twin API", version: str = "1.0.0") -> FastAPI:
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
        repository.get_appliances(), repository.get_routines())

    api = FastAPI(
        title=title,
        version=version,
        docs_url="/api",
        redoc_url=None
    )

    if serve_static:
        api.mount("/", StaticFiles(directory=serve_dir,
                  html=True), name="static")

    @api.get("/api/consumption/{when}", tags=[__CONSUMPTION_TAG])
    async def get_consumption_total(when: datetime) -> float:
        """Get the total consumption at a given date and time.

        **Args**:
        - `when (datetime)`: The date and time.

        **Returns**:
        - `float`: The total consumption at the given date and time, in watts.
        """

        return matrix.total_consumption(when)

    @api.post("/api/consumption/{when}", tags=[__CONSUMPTION_TAG])
    async def post_consumption_total(when: datetime, routine_in: RoutineIn) -> float:
        return matrix.simulate(__routine_schema_to_model(routine_in, repository)).total_consumption(when)

    @api.get("/api/consumption/{appliance_id}/{when}", tags=[__CONSUMPTION_TAG])
    async def get_appliance_consumption(appliance_id: int, when: datetime) -> float:
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

    @api.post("/api/consumption/{appliance_id}/{when}", tags=[__CONSUMPTION_TAG])
    async def post_appliance_consumption(appliance_id: int, when: datetime, routine_in: RoutineIn) -> float:
        appliance = repository.get_appliance(appliance_id)

        if appliance is None:
            raise errors.APPLIANCE_NOT_FOUND

        return matrix.simulate(__routine_schema_to_model(routine_in, repository)).consumption(appliance, when)

    @api.get("/api/appliance/{appliance_id}", tags=[__APPLIANCE_TAG])
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

    @api.get("/api/appliance", tags=[__APPLIANCE_TAG])
    async def get_appliances() -> list[ApplianceOut]:
        """Get all appliances.

        **Returns**:
        - `list[ApplianceOut]`: The appliances.
        """

        return [ApplianceOut.model_validate(a) for a in repository.get_appliances()]

    @api.get("/api/routine/{routine_id}", tags=[__ROUTINE_TAG])
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

    @api.get("/api/routine", tags=[__ROUTINE_TAG])
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
