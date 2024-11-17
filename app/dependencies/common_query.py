from typing import Annotated
from fastapi import APIRouter, Depends, Cookie, Header, HTTPException


# dependencies injection/resources/providers/services/injectables/components

# Have shared logic (the same code logic again and again).
# Share database connections.
# Enforce security, authentication, role requirements, etc.


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


CommonQueryParams = Annotated[dict, Depends(CommonQueryParams)]


# Sub-dependencies
def query_extractor(q: str | None = None):
    return q


def query_or_cookie_extractor(
    q: Annotated[str, Depends(query_extractor)],
    last_query: Annotated[str | None, Cookie()] = None,
):
    if not q:
        return last_query
    return q
