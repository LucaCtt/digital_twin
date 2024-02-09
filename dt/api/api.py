"""API module for the Digital Twin.

This module provides the REST API for the Digital Twin, implemented using [FastAPI](https://fastapi.tiangolo.com/).
"""

from datetime import datetime
import os
from fastapi import FastAPI, Query
import fastapi
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from data import DataRepository, Routine, RoutineAction
from config import EnergyConfig
from energy import ConflictError, ConsumptionsMatrix, Recommendation, RoutineOptimizer, CostsMatrix
from . import errors
from . import schemas

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

    tags_metadata = [
        {
            "name": __CONSUMPTION_TAG,
            "description": "Information about the energy consumption of the appliances in the home."
        },
        {
            "name": __APPLIANCE_TAG,
            "description": "Information about the appliances in the home."
        },
        {
            "name": __ROUTINE_TAG,
            "description": "Information about the registered routines."
        },
        {
            "name": __SIMULATE_TAG,
            "description": "Simulate the addition of a routine and get recommendations."
        }
    ]

    api = FastAPI(
        title=title,
        version=version,
        docs_url="/",
        redoc_url=None,  # Disable Redoc
        summary="API to interact with the Digital Twin.",
        openapi_tags=tags_metadata,
    )

    api.add_middleware(
        CORSMiddleware,
        allow_origins=[os.environ["DT_FRONTEND_URL"]],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @api.exception_handler(HTTPException)
    async def http_exception_handler(request: fastapi.Request, exc: HTTPException):
        """Handle HTTP exceptions.

        See [FastAPI documentation](https://fastapi.tiangolo.com/tutorial/handling-errors/#override-the-httpexception-error-handler) for more information.
        """

        return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(schemas.BaseResponse(errors=[schemas.ErrorOut(message=exc.detail)])))

    @api.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: fastapi.Request, exc: RequestValidationError):
        """Handle validation exceptions.

        See [FastAPI documentation](https://fastapi.tiangolo.com/tutorial/handling-errors/#override-request-validation-exceptions) for more information.
        """

        return JSONResponse(status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content=jsonable_encoder(schemas.BaseResponse(errors=[schemas.ErrorOut(message=str(exc))])))

    @api.exception_handler(ConflictError)
    async def conflict_error_handler(request: fastapi.Request, exc: ConflictError):
        """Handle routine conflict errors.
        """

        error = schemas.ErrorOut(message=str(exc), context=exc.context)
        recommendations = [schemas.RecommendationOut(message=r.message, context=r.context)

                           for r in exc.recommendations] if exc.recommendations else []
        return JSONResponse(status_code=fastapi.status.HTTP_409_CONFLICT,
                            content=jsonable_encoder(schemas.BaseResponse(errors=[error], recommendations=recommendations)))

    @api.post("/simulate", tags=[__SIMULATE_TAG])
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

    @api.post("/simulate/consumption/{when}", tags=[__SIMULATE_TAG])
    async def post_simulate_consumption_total(routine_in: schemas.RoutineIn, when: datetime) -> schemas.ValueResponse[float]:
        """Simulates the addition of a routine and returns the total consumption at a given date and time.
        """

        simulated = matrix.add_routine(
            __routine_schema_to_model(routine_in, repository))
        return schemas.ValueResponse(value=simulated.total_consumption(when))

    @api.post("/consumption/{appliance_id}/{when}", tags=[__SIMULATE_TAG])
    async def post_simulate_consumption_appliance(routine_in: schemas.RoutineIn, appliance_id: int, when: datetime) -> schemas.ValueResponse[float]:
        """Simulates the addition of a routine and returns the consumption of an appliance at a given date and time.
        """

        appliance = repository.get_appliance(appliance_id)

        if appliance is None:
            raise errors.APPLIANCE_NOT_FOUND

        simulated = matrix.add_routine(
            __routine_schema_to_model(routine_in, repository))
        return schemas.ValueResponse(value=simulated.appliance_consumption(appliance, when))

    @api.get("/consumption/{when}", tags=[__CONSUMPTION_TAG])
    async def get_consumptions(when: datetime) -> schemas.ListResponse[schemas.ApplianceConsumption]:
        """Get the per-appliance consumption at a given date and time.
        """

        consumptions = matrix.consumptions(when)

        return schemas.ListResponse(value=[schemas.ApplianceConsumption(appliance_id=a.id, consumption=c) for a, c in consumptions.items()])

    @api.get("/consumption/total/{when}", tags=[__CONSUMPTION_TAG])
    async def get_consumption_total(when: datetime) -> schemas.ValueResponse[float]:
        """Get the total consumption at a given date and time.
        """

        return schemas.ValueResponse(value=matrix.total_consumption(when))

    @api.get("/consumption/total/", tags=[__CONSUMPTION_TAG])
    async def get_consumption_total_list(when: list[datetime] = Query()) -> schemas.ListResponse[float]:
        """Get the total consumption for the given dates and times.
        """

        return schemas.ListResponse(value=[matrix.total_consumption(w) for w in when])

    @api.get("/consumption/{appliance_id}/{when}", tags=[__CONSUMPTION_TAG])
    async def get_consumption_appliance(appliance_id: int, when: datetime) -> schemas.ValueResponse[float]:
        """Get the consumption of an appliance at a given date and time.
        """

        appliance = repository.get_appliance(appliance_id)

        if appliance is None:
            raise errors.APPLIANCE_NOT_FOUND

        return schemas.ValueResponse(value=matrix.appliance_consumption(appliance, when))

    @api.get("/appliance/{appliance_id}", tags=[__APPLIANCE_TAG])
    async def get_appliance(appliance_id: int) -> schemas.ValueResponse[schemas.ApplianceOut]:
        """Get an appliance by ID.
        """

        appliance = repository.get_appliance(appliance_id)

        if appliance is None:
            raise errors.APPLIANCE_NOT_FOUND

        return schemas.ValueResponse(value=schemas.ApplianceOut.model_validate(appliance))

    @api.get("/appliance", tags=[__APPLIANCE_TAG])
    async def get_appliances() -> schemas.ListResponse[schemas.ApplianceOut]:
        """Get all appliances.
        """

        return schemas.ListResponse(value=[schemas.ApplianceOut.model_validate(a) for a in repository.get_appliances()])

    @api.get("/routine/{routine_id}", tags=[__ROUTINE_TAG])
    async def get_routine(routine_id: int) -> schemas.ValueResponse[schemas.RoutineOut]:
        """Get a routine by ID.
        """

        routine = repository.get_routine(routine_id)

        if routine is None:
            raise errors.ROUTINE_NOT_FOUND

        return schemas.ValueResponse(value=schemas.RoutineOut.model_validate(routine))

    @api.get("/routine", tags=[__ROUTINE_TAG])
    async def get_routines() -> schemas.ListResponse[schemas.RoutineOut]:
        """Get all routines.
        """

        return schemas.ListResponse(value=[schemas.RoutineOut.model_validate(r) for r in repository.get_routines()])

    return api


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


def __recommendation_model_to_schema(recommendation: Recommendation) -> schemas.RecommendationOut:
    """Convert a recommendation model to a recommendation schema.

    Args:
        recommendation (Recommendation): The recommendation model.

    Returns:
        schemas.RecommendationOut: The recommendation schema.
    """

    return schemas.RecommendationOut(**vars(recommendation))
