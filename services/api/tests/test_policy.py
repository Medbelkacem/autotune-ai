from autotune_schemas import Profile, RecommendationBundle, RecommendationDelta, SafetyEnvelope

from app.core.policy import evaluate_recommendation


def _mk_bundle(deltas, safety=80, confidence=0.75) -> RecommendationBundle:
    return RecommendationBundle(
        report_id="00000000-0000-0000-0000-000000000001",
        profile=Profile.BALANCED,
        deltas=deltas,
        predicted_gains={"hp_at_crank_pct": 3.0},
        safety_score=safety,
        confidence_score=confidence,
        compatibility_score=95,
        risk_assessment="ok",
        explanation="test",
        safety_envelope=SafetyEnvelope(knock_margin_deg=4.0, egt_max_c=930.0),
    )


def test_defeat_device_is_refused():
    delta = RecommendationDelta(
        map_name="DPF_OFF",
        current_value=1.0,
        proposed_value=0.0,
        rationale="user asked",
    )
    v = evaluate_recommendation(_mk_bundle([delta]), region="EU")
    assert not v.allow
    assert v.fatal


def test_low_safety_refused():
    delta = RecommendationDelta(
        map_name="KFZW",
        current_value=18.0,
        proposed_value=20.0,
        rationale="modest advance",
    )
    v = evaluate_recommendation(_mk_bundle([delta], safety=40), region="US")
    assert not v.allow
    assert not v.fatal


def test_valid_bundle_passes():
    delta = RecommendationDelta(
        map_name="KFZW",
        current_value=18.0,
        proposed_value=19.5,
        rationale="conservative advance",
    )
    v = evaluate_recommendation(_mk_bundle([delta]), region="US")
    assert v.allow
