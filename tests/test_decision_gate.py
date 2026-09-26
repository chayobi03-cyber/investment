from src.investment_pipeline.decision_gate import (
    BUY_ALLOWED,
    EXECUTION_ALLOWED,
    DecisionGateAgent,
    DecisionState,
)


def test_all_green_is_research_only_until_promotion():
    result = DecisionGateAgent().run({
        "data_pit": "PASS", "regime": "PASS", "permission": "PASS",
        "risk": "PASS", "evidence": "PASS", "source_retrieval": "PASS",
        "source_quality": "PASS", "conflict": "PASS",
        "hallucination": "PASS", "signal": "PASS",
    })
    assert result.decision_status == DecisionState.RESEARCH_ONLY
    assert result.promotion_status == "DISABLED"
    assert result.buy_allowed is False
    assert result.execution_allowed is False


def test_blocked_upstream_is_blocked():
    result = DecisionGateAgent().run({"data_pit": "PASS", "permission": "BLOCKED", "risk": "PASS"}, blocker_codes=("MACRO_BLOCK",))
    assert result.decision_status == DecisionState.BLOCKED
    assert result.blocker_codes == ("MACRO_BLOCK",)


def test_data_not_ready_dominates_blocked():
    result = DecisionGateAgent().run({"data_pit": "DATA_NOT_READY", "permission": "BLOCKED"}, blocker_codes=("PIT_GATE_NOT_GREEN",))
    assert result.decision_status == DecisionState.DATA_NOT_READY


def test_global_execution_locks_are_immutable_false():
    assert BUY_ALLOWED is False
    assert EXECUTION_ALLOWED is False
