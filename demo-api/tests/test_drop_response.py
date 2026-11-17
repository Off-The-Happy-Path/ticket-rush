from app.faults import fault_log, should_drop


def test_drop_decision_is_repeatable():
    fault_log.reset()
    first = [should_drop("/reservations", "fan-1", 20, 7) for _ in range(50)]
    fault_log.reset()
    second = [should_drop("/reservations", "fan-1", 20, 7) for _ in range(50)]
    assert first == second
    assert 0 < sum(first) < 50


def test_zero_percent_never_drops():
    fault_log.reset()
    assert not any(should_drop("/orders", f"fan-{i}", 0, 0) for i in range(200))


def test_report_has_retried_duplicates_when_off(client):
    report = client.get("/admin/report").json()
    assert report["retried_duplicates_total"] == 0
    assert report["responses_dropped_after_commit"] == 0
