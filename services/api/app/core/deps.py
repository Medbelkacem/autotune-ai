"""FastAPI dependencies — auth, current user, RBAC."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import decode_token


class CurrentUser:
    def __init__(self, user_id: UUID, org_id: UUID, roles: list[str], raw: dict):
        self.user_id = user_id
        self.org_id = org_id
        self.roles = roles
        self.raw = raw

    def has_role(self, *roles: str) -> bool:
        return any(r in self.roles for r in roles)


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> CurrentUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token, expected_type="access")
    except ValueError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e
    try:
        return CurrentUser(
            user_id=UUID(payload["sub"]),
            org_id=UUID(payload["org"]),
            roles=list(payload.get("roles", [])),
            raw=payload,
        )
    except (KeyError, ValueError) as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "malformed token") from e


def require_role(*required: str):
    async def _dep(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if not user.has_role(*required):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"requires one of: {', '.join(required)}",
            )
        return user
    return _dep


DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
