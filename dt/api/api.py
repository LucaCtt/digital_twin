"""API module for the Digital Twin.

This module provides the REST API for the Digital Twin, implemented using [FastAPI](https://fastapi.tiangolo.com/).
"""

import os
from fastapi import FastAPI
import fastapi
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException

from dt.data import DataRepository
from dt.config import EnergyConfig
from dt.energy import ConflictError, ConsumptionsMatrix, CostsMatrix
from . import routes
from . import schemas

__CONSUMPTION_TAG = "Consumption"
__APPLIANCE_TAG = "Appliance"
__ROUTINE_TAG = "Routine"
__SIMULATE_TAG = "Simulation"

TAGS_METADATA = [
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
        redoc_url=None,  # Disable Redoc
        summary="API to interact with the Digital Twin.",
        openapi_tags=TAGS_METADATA,
    )

    api.add_middleware(
        CORSMiddleware,
        allow_origins=[os.environ["DT_FRONTEND_URL"]],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api.include_router(routes.get_appliance_router(
        repository, tags=[__APPLIANCE_TAG]))
    api.include_router(routes.get_routine_router(
        repository, tags=[__ROUTINE_TAG]))
    api.include_router(routes.get_consumption_router(
        repository, matrix, tags=[__CONSUMPTION_TAG]))
    api.include_router(routes.get_simulate_router(
        repository, matrix, costs, tags=[__SIMULATE_TAG]))

    @api.exception_handler(HTTPException)
    async def http_exception_handler(_: fastapi.Request, exc: HTTPException):
        """Handle HTTP exceptions.

        See [FastAPI documentation](https://fastapi.tiangolo.com/tutorial/handling-errors/#override-the-httpexception-error-handler) for more information.
        """

        return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(schemas.BaseResponse(errors=[schemas.ErrorOut(message=exc.detail)])))

    @api.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: fastapi.Request, exc: RequestValidationError):
        """Handle validation exceptions.

        See [FastAPI documentation](https://fastapi.tiangolo.com/tutorial/handling-errors/#override-request-validation-exceptions) for more information.
        """

        return JSONResponse(status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content=jsonable_encoder(schemas.BaseResponse(errors=[schemas.ErrorOut(message=str(exc))])))

    @api.exception_handler(ConflictError)
    async def conflict_error_handler(_: fastapi.Request, exc: ConflictError):
        """Handle routine conflict errors.
        """

        error = schemas.ErrorOut(message=str(exc), context=exc.context)
        recommendations = [schemas.RecommendationOut(message=r.message, context=r.context)

                           for r in exc.recommendations] if exc.recommendations else []
        return JSONResponse(status_code=fastapi.status.HTTP_409_CONFLICT,
                            content=jsonable_encoder(schemas.BaseResponse(errors=[error], recommendations=recommendations)))

    return api
