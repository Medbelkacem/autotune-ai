from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.config import get_settings
from app.core.deps import CurrentUserDep, DbSession
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import Organization, Role, RoleAssignment, Session, User
from app.schemas.auth import (
    LoginRequest,
    MeResponse,
    RefreshRequest,
    SignupRequest,
    TokenPair,
)

router = APIRouter()
_settings = get_settings()


@router.post("/signup", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, db: DbSession) -> TokenPair:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "email already in use")

    org = Organization(name=payload.organization_name, plan="free", region=payload.region)
    db.add(org)
    await db.flush()

    user = User(
        org_id=org.id,
        email=payload.email,
        name=payload.name,
        pwd_hash=hash_password(payload.password),
        status="active",
    )
    db.add(user)
    await db.flush()

    # Grant 'owner' role
    owner = (
        await db.execute(select(Role).where(Role.name == "owner"))
    ).scalar_one_or_none()
    if owner is None:
        owner = Role(name="owner")
        db.add(owner)
        await db.flush()
    db.add(RoleAssignment(user_id=user.id, role_id=owner.id, scope="org"))

    await db.commit()
    return _issue_tokens(db, user, roles=["owner"])


@router.post("/login", response_model=TokenPair)
async def login(payload: LoginRequest, db: DbSession) -> TokenPair:
    res = await db.execute(select(User).where(User.email == payload.email))
    user = res.scalar_one_or_none()
    if not user or not user.pwd_hash or not verify_password(payload.password, user.pwd_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")
    if user.status != "active":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "account is not active")

    if user.totp_enrolled:
        if not payload.totp_code:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "MFA code required")
        from app.core.mfa import totp_verify

        if not user.mfa_secret or not totp_verify(user.mfa_secret, payload.totp_code):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid TOTP code")

    user.last_login_at = datetime.now(timezone.utc)

    roles = [
        r[0]
        for r in (
            await db.execute(
                select(Role.name)
                .join(RoleAssignment, RoleAssignment.role_id == Role.id)
                .where(RoleAssignment.user_id == user.id)
            )
        ).all()
    ]
    tokens = await _issue_tokens(db, user, roles=roles or ["viewer"])
    await db.commit()
    return tokens


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, db: DbSession) -> TokenPair:
    try:
        claims = decode_token(payload.refresh_token, expected_type="refresh")
    except ValueError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e

    jti = claims["jti"]
    res = await db.execute(select(Session).where(Session.refresh_token_jti == jti))
    sess = res.scalar_one_or_none()
    if not sess or sess.revoked_at:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "refresh token revoked")

    user = (await db.execute(select(User).where(User.id == sess.user_id))).scalar_one()
    roles = [
        r[0]
        for r in (
            await db.execute(
                select(Role.name)
                .join(RoleAssignment, RoleAssignment.role_id == Role.id)
                .where(RoleAssignment.user_id == user.id)
            )
        ).all()
    ]
    # rotate
    sess.revoked_at = datetime.now(timezone.utc)
    tokens = await _issue_tokens(db, user, roles=roles)
    await db.commit()
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshRequest, db: DbSession) -> None:
    try:
        claims = decode_token(payload.refresh_token, expected_type="refresh")
    except ValueError:
        return
    res = await db.execute(select(Session).where(Session.refresh_token_jti == claims["jti"]))
    sess = res.scalar_one_or_none()
    if sess and not sess.revoked_at:
        sess.revoked_at = datetime.now(timezone.utc)
        await db.commit()


@router.get("/me", response_model=MeResponse)
async def me(user: CurrentUserDep, db: DbSession) -> MeResponse:
    u = (await db.execute(select(User).where(User.id == user.user_id))).scalar_one()
    org = (await db.execute(select(Organization).where(Organization.id == u.org_id))).scalar_one()
    return MeResponse(
        user_id=u.id,
        email=u.email,
        name=u.name,
        org_id=org.id,
        org_name=org.name,
        roles=user.roles,
    )


async def _issue_tokens(db, user: User, *, roles: list[str]) -> TokenPair:
    access = create_access_token(subject=user.id, org_id=user.org_id, roles=roles)
    refresh_token = create_refresh_token(subject=user.id)
    claims = decode_token(refresh_token, expected_type="refresh")
    db.add(
        Session(
            id=uuid4(),
            user_id=user.id,
            refresh_token_jti=claims["jti"],
            expires_at=datetime.now(timezone.utc)
            + timedelta(seconds=_settings.jwt_refresh_ttl_seconds),
        )
    )
    return TokenPair(
        access_token=access,
        refresh_token=refresh_token,
        expires_in=_settings.jwt_access_ttl_seconds,
    )
