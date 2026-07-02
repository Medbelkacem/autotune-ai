from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.core.deps import CurrentUserDep, DbSession
from app.core.mfa import new_secret, provisioning_uri, totp_verify
from app.models import User

router = APIRouter()


class EnrollResponse(BaseModel):
    provisioning_uri: str
    secret_b32: str


class VerifyRequest(BaseModel):
    code: str


@router.post("/enroll", response_model=EnrollResponse)
async def enroll(user: CurrentUserDep, db: DbSession) -> EnrollResponse:
    u = (await db.execute(select(User).where(User.id == user.user_id))).scalar_one()
    if u.totp_enrolled:
        raise HTTPException(status.HTTP_409_CONFLICT, "TOTP already enrolled")
    sec = new_secret()
    u.mfa_secret = sec  # stored raw for dev; production wraps with KMS envelope encryption
    await db.commit()
    import base64

    return EnrollResponse(
        provisioning_uri=provisioning_uri(
            email=u.email, issuer="AutoTune AI", secret=sec,
        ),
        secret_b32=base64.b32encode(sec).decode().rstrip("="),
    )


@router.post("/verify", status_code=status.HTTP_204_NO_CONTENT)
async def verify(payload: VerifyRequest, user: CurrentUserDep, db: DbSession) -> None:
    u = (await db.execute(select(User).where(User.id == user.user_id))).scalar_one()
    if not u.mfa_secret:
        raise HTTPException(status.HTTP_412_PRECONDITION_FAILED, "no TOTP secret; call /enroll")
    if not totp_verify(u.mfa_secret, payload.code):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid TOTP code")
    if not u.totp_enrolled:
        u.totp_enrolled = True
        await db.commit()
