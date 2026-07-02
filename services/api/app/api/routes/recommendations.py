from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import CurrentUserDep, DbSession, require_role
from app.core.policy import evaluate_recommendation
from app.core.security import verify_signature
from app.models import AnalysisReport, Recommendation, ScanSession, User, Vehicle
from app.schemas.recommendation import (
    ApprovalRequest,
    RecommendationOut,
    RecommendationRequest,
)

router = APIRouter()


@router.post("", response_model=RecommendationOut, status_code=status.HTTP_201_CREATED)
async def generate(
    payload: RecommendationRequest, user: CurrentUserDep, db: DbSession
) -> RecommendationOut:
    row = (
        await db.execute(
            select(AnalysisReport, Vehicle)
            .join(ScanSession, ScanSession.id == AnalysisReport.scan_id)
            .join(Vehicle, Vehicle.id == ScanSession.vehicle_id)
            .where(AnalysisReport.id == payload.report_id, Vehicle.org_id == user.org_id)
        )
    ).first()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "report not found")

    # Full multi-agent pipeline (strategist → verifier → compliance → explainer).
    # Falls back to the single-agent orchestrator if the full path is disabled.
    from app.ai.orchestrator2 import run_full_pipeline

    bundle = await run_full_pipeline(
        report=row[0],
        profile=payload.profile,
        region="US",  # TODO: resolve from org.region
    )

    rec = Recommendation(
        report_id=row[0].id,
        safety_score=bundle.safety_score,
        confidence_score=bundle.confidence_score,
        compat_score=bundle.compatibility_score,
        predicted_gains=bundle.predicted_gains,
        bundle=bundle.model_dump(mode="json"),
        status=bundle.status,
    )
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return RecommendationOut.model_validate(rec)


@router.get("/{rec_id}", response_model=RecommendationOut)
async def get_recommendation(
    rec_id: UUID, user: CurrentUserDep, db: DbSession
) -> RecommendationOut:
    row = (
        await db.execute(
            select(Recommendation, Vehicle)
            .join(AnalysisReport, AnalysisReport.id == Recommendation.report_id)
            .join(ScanSession, ScanSession.id == AnalysisReport.scan_id)
            .join(Vehicle, Vehicle.id == ScanSession.vehicle_id)
            .where(Recommendation.id == rec_id, Vehicle.org_id == user.org_id)
        )
    ).first()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "recommendation not found")
    return RecommendationOut.model_validate(row[0])


@router.post("/{rec_id}/approve", response_model=RecommendationOut)
async def approve(
    rec_id: UUID,
    payload: ApprovalRequest,
    user: CurrentUserDep = require_role("tuner", "owner", "admin"),  # noqa: B008
    db: DbSession = None,  # type: ignore[assignment]
) -> RecommendationOut:
    row = (
        await db.execute(
            select(Recommendation, Vehicle)
            .join(AnalysisReport, AnalysisReport.id == Recommendation.report_id)
            .join(ScanSession, ScanSession.id == AnalysisReport.scan_id)
            .join(Vehicle, Vehicle.id == ScanSession.vehicle_id)
            .where(Recommendation.id == rec_id, Vehicle.org_id == user.org_id)
        )
    ).first()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "recommendation not found")
    rec: Recommendation = row[0]

    # Lookup tuner public key by fingerprint (omitted: key registry).
    # For now we re-verify against a key stored on the user record.
    from autotune_schemas import RecommendationBundle

    bundle = RecommendationBundle.model_validate(rec.bundle)

    # Region-aware policy gate
    org_region = "US"  # could be fetched from org row
    verdict = evaluate_recommendation(bundle, region=org_region)
    if not verdict.allow:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"policy refused approval: {verdict.reason}",
        )

    # Verify ed25519 signature against the canonical JSON of the bundle.
    canonical = json.dumps(rec.bundle, sort_keys=True, separators=(",", ":")).encode()
    u = (
        await db.execute(select(User).where(User.id == user.user_id))
    ).scalar_one()
    public_key = (u.webauthn or {}).get("ed25519_public_b64")
    if not public_key:
        raise HTTPException(
            status.HTTP_412_PRECONDITION_FAILED,
            "no signing key registered for approver",
        )
    if not verify_signature(canonical, payload.signature_b64, public_key):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid signature")

    rec.status = "approved"
    rec.approved_by = user.user_id
    rec.signed_blob = payload.signature_b64.encode()
    bundle_dict = dict(rec.bundle)
    bundle_dict["status"] = "approved"
    bundle_dict["approval"] = {
        "signer_user_id": str(user.user_id),
        "signer_role": "tuner",
        "algorithm": "ed25519",
        "signed_at": datetime.now(timezone.utc).isoformat(),
        "signature_b64": payload.signature_b64,
        "key_fingerprint": payload.key_fingerprint,
    }
    rec.bundle = bundle_dict
    await db.commit()
    await db.refresh(rec)
    return RecommendationOut.model_validate(rec)
