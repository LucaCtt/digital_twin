from dt.api import create_api
from dt.consumptions import ConsumptionsMatrix
from dt.data import JSONRepository
from dt import const

repository = JSONRepository(
    const.APPLIANCES_DIR, const.ROUTINES_DIR, const.TEST_ROUTINES_DIR)
matrix = ConsumptionsMatrix(
    repository.get_appliances(), repository.get_routines())

api = create_api(repository, matrix, version="1.0.0")
