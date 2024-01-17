"""Error codes for the API.
"""

from fastapi import HTTPException, status


APPLIANCE_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Appliance not found")

ROUTINE_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Routine not found")

APPLIANCE_INVALID = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid appliance")

OPERATION_MODE_INVALID = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid operation mode")
