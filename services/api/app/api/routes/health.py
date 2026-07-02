from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz", include_in_schema=False)
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz", include_in_schema=False)
async def readiness() -> dict[str, str]:
    # extend with DB/Redis pings
    return {"status": "ready"}


@router.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {"name": "autotune-ai", "docs": "/docs"}
