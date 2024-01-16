from datetime import datetime
from fastapi import FastAPI, HTTPException
from data import DataRepository
from consumptions import ConsumptionsMatrix
from .schemas import ApplianceBase, RoutineBase

ERR_APPLIANCE_NOT_FOUND = HTTPException(
    status_code=404, detail="Appliance not found")
ERR_ROUTINE_NOT_FOUND = HTTPException(
    status_code=404, detail="Routine not found")


def create_api(repository: DataRepository, matrix: ConsumptionsMatrix, title="Digital Twin API", version: str = "1.0.0") -> FastAPI:
    """Create a FastAPI instance.

    Create a new FastAPI instance, using the given data repository and
    consumptions matrix. These are not passed to routes using dependency injection
    as they are global to the application.

    Args:
        repository (DataRepository): The data repository.
        matrix (ConsumptionsMatrix): The consumptions matrix.
        title (str, optional): The API title. Defaults to "Digital Twin API".
        version (str, optional): The API version. Defaults to "1.0.0". Remember to update this value when you make changes to the API.
        Please follow the [Semantic Versioning](https://semver.org/) guidelines.

    Raises:
        ERR_APPLIANCE_NOT_FOUND: _description_
        ERR_APPLIANCE_NOT_FOUND: _description_
        ERR_ROUTINE_NOT_FOUND: _description_

    Returns:
        FastAPI: The FastAPI instance.
    """

    api = FastAPI(
        title=title,
        version=version,
    )

    @api.get("/consumption/{when}")
    async def consumption_total(when: datetime) -> float:
        """Get the total consumption of all appliances at a given date and time.
        """
        return matrix.total_consumption(when)

    @api.get("/consumption/{appliance_id}/{when}")
    async def appliance_consumption(appliance_id: int, when: datetime) -> float:
        """Get the consumption of a given appliance at a given date and time.
        """
        appliance = repository.get_appliance(appliance_id)

        if appliance is None:
            raise ERR_APPLIANCE_NOT_FOUND

        return matrix.consumption(appliance, when)

    @api.get("/appliances/{appliance_id}")
    async def get_appliance(appliance_id: int) -> ApplianceBase:
        """Get an appliance by ID.
        """

        appliance = repository.get_appliance(appliance_id)

        if appliance is None:
            raise ERR_APPLIANCE_NOT_FOUND

        return ApplianceBase.model_validate(appliance)

    @api.get("/appliances")
    async def get_appliances() -> list[ApplianceBase]:
        """Get all appliances.
        """
        return [ApplianceBase.model_validate(a) for a in repository.get_appliances()]

    @api.get("/routines/{routine_id}")
    async def get_routine(routine_id: int) -> RoutineBase:
        """Get a routine by ID.
        """
        routine = repository.get_routine(routine_id)

        if routine is None:
            raise ERR_ROUTINE_NOT_FOUND

        return RoutineBase.model_validate(routine)

    @api.get("/routines")
    async def get_routines() -> list[RoutineBase]:
        """Get all routines.
        """
        return [RoutineBase.model_validate(r) for r in repository.get_routines()]

    @api.post("/simulate")
    async def simulate(routine: RoutineBase) -> list[str]:
        return []

    return api
