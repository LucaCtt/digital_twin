from api import create_api
from consumptions import ConsumptionsMatrix
from data import JSONRepository
import const

repository = JSONRepository(
    const.APPLIANCES_DIR, const.ROUTINES_DIR, const.TEST_ROUTINES_DIR)
matrix = ConsumptionsMatrix(
    repository.get_appliances(), repository.get_routines())

api = create_api(repository, matrix, version="1.0.0")
