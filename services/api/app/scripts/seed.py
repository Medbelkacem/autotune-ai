"""Seed demo data — organizations, users, roles, vehicles, KB docs."""

from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select

from app.core.db import session_factory
from app.core.security import hash_password
from app.models import (
    Organization,
    Permission,
    Role,
    RoleAssignment,
    RolePermission,
    User,
    Vehicle,
)


ROLES = ["owner", "admin", "tuner", "technician", "viewer", "auditor"]

PERMISSIONS = [
    ("vehicle:read", "Read vehicles"),
    ("vehicle:write", "Create/update vehicles"),
    ("ecu:read", "Read ECU calibration data"),
    ("ecu:write", "Flash ECU (authorized tuner only)"),
    ("recommendation:generate", "Generate recommendations"),
    ("recommendation:approve", "Approve a recommendation with signature"),
    ("telemetry:read", "Read live telemetry"),
    ("billing:manage", "Manage subscription and billing"),
    ("org:admin", "Administer the organization"),
]

# role -> permissions (subset)
ROLE_MATRIX = {
    "owner": [p[0] for p in PERMISSIONS],
    "admin": [
        "vehicle:read", "vehicle:write", "ecu:read",
        "recommendation:generate", "telemetry:read", "org:admin",
    ],
    "tuner": [
        "vehicle:read", "vehicle:write", "ecu:read", "ecu:write",
        "recommendation:generate", "recommendation:approve", "telemetry:read",
    ],
    "technician": [
        "vehicle:read", "vehicle:write", "ecu:read",
        "recommendation:generate", "telemetry:read",
    ],
    "viewer": ["vehicle:read", "telemetry:read"],
    "auditor": ["vehicle:read", "ecu:read", "recommendation:generate"],
}


async def _ensure_roles_and_permissions(db) -> dict[str, Role]:
    roles: dict[str, Role] = {}
    for name in ROLES:
        r = (await db.execute(select(Role).where(Role.name == name))).scalar_one_or_none()
        if r is None:
            r = Role(name=name)
            db.add(r)
            await db.flush()
        roles[name] = r

    perms: dict[str, Permission] = {}
    for code, desc in PERMISSIONS:
        p = (
            await db.execute(select(Permission).where(Permission.code == code))
        ).scalar_one_or_none()
        if p is None:
            p = Permission(code=code, description=desc)
            db.add(p)
            await db.flush()
        perms[code] = p

    for role_name, code_list in ROLE_MATRIX.items():
        r = roles[role_name]
        for code in code_list:
            p = perms[code]
            existing = (
                await db.execute(
                    select(RolePermission).where(
                        RolePermission.role_id == r.id,
                        RolePermission.permission_id == p.id,
                    )
                )
            ).first()
            if not existing:
                db.add(RolePermission(role_id=r.id, permission_id=p.id))
    return roles


async def _ensure_demo_org(db, roles) -> Organization:
    org = (
        await db.execute(select(Organization).where(Organization.name == "Demo Workshop"))
    ).scalar_one_or_none()
    if org is None:
        org = Organization(name="Demo Workshop", plan="workshop", region="US")
        db.add(org)
        await db.flush()

    owner_email = "owner@demo.autotune.ai"
    owner = (await db.execute(select(User).where(User.email == owner_email))).scalar_one_or_none()
    if owner is None:
        owner = User(
            org_id=org.id,
            email=owner_email,
            name="Demo Owner",
            pwd_hash=hash_password("demo-owner-Pass!23"),
            status="active",
        )
        db.add(owner)
        await db.flush()
        db.add(RoleAssignment(user_id=owner.id, role_id=roles["owner"].id, scope="org"))

    tuner_email = "tuner@demo.autotune.ai"
    tuner = (await db.execute(select(User).where(User.email == tuner_email))).scalar_one_or_none()
    if tuner is None:
        tuner = User(
            org_id=org.id,
            email=tuner_email,
            name="Demo Tuner",
            pwd_hash=hash_password("demo-tuner-Pass!23"),
            status="active",
        )
        db.add(tuner)
        await db.flush()
        db.add(RoleAssignment(user_id=tuner.id, role_id=roles["tuner"].id, scope="org"))

    return org


async def _seed_vehicles(db, org: Organization) -> None:
    demo_vins = [
        ("WAUZZZ8K9BA123456", "Audi", "A4 Avant", 2014, "CAEB", "0B5", "Gasoline_RON95", "EU5"),
        ("WBSWD9C50BE123457", "BMW", "M3 F80", 2016, "S55B30", "GS7D36BG", "Gasoline_RON98", "EU6"),
        ("1FT8W3BT9NEB12345", "Ford", "F-150 PowerStroke", 2022, "3.0L PS", "10R80", "Diesel_ULSD", "Tier3"),
    ]
    for vin, mfr, model, year, engine, trans, fuel, emis in demo_vins:
        exists = (
            await db.execute(
                select(Vehicle).where(Vehicle.org_id == org.id, Vehicle.vin == vin)
            )
        ).scalar_one_or_none()
        if not exists:
            db.add(
                Vehicle(
                    id=uuid.uuid4(),
                    org_id=org.id,
                    vin=vin,
                    manufacturer=mfr,
                    model=model,
                    year=year,
                    engine_code=engine,
                    transmission_code=trans,
                    fuel_type=fuel,
                    emission_standard=emis,
                )
            )


async def main() -> None:
    async with session_factory()() as db:
        roles = await _ensure_roles_and_permissions(db)
        org = await _ensure_demo_org(db, roles)
        await _seed_vehicles(db, org)
        await db.commit()
        print("Seeded demo data.")


if __name__ == "__main__":
    asyncio.run(main())
