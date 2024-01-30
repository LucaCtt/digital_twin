"""Module for data access.

This module provides utilities to access the data of the digital twin.
The data is supposed to be read only, as it is not meant to be modified by the digital twin.
"""

from .data_repository import DataRepository, JSONRepository, RepositoryFactory
from .models import *
